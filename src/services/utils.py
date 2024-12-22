import datetime as dt
import os
import zipfile
from logging import getLogger
from typing import Dict, List

import tiktoken
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_community.chat_models import ChatOpenAI
from openai import OpenAI

from src.config.config import app_settings
from src.config.logging_config import LOG_DIR

logger = getLogger(__name__)


def generate_summary(text: str, prompt: str) -> str:
    full_prompt = f"{prompt}\n\n{text}"
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    pages = text_splitter.split_text(full_prompt)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.create_documents(pages)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0301")
    chain = load_summarize_chain(llm, chain_type="refine")

    content_summary = chain.run(texts)
    return content_summary


def summarize_text(
    article_text: str,
    system_prompt: str,
) -> str:
    """
    Calls LLM using system prompt and article's text message.
    Language model and system prompt are specified in .env configuration file.
    """
    if not article_text:
        logger.info("Article text is empty. SKIPPING")
        return ""

    model = app_settings.LANGUAGE_MODEL
    start_time = dt.datetime.now()

    full_prompt = f"{system_prompt}\n\n{article_text}"
    n_tokens = num_tokens_from_string(full_prompt, model)

    if n_tokens > 128000:
        # Step 1: Split the article into manageable chunks
        chunk_size = get_chunk_size(article_text, app_settings.LANGUAGE_MODEL)
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_size // 10
        )
        chunks = text_splitter.split_text(article_text)

        chunk_summaries = []

        # Step 2: Generate summaries for each chunk
        for chunk in chunks:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk},
            ]
            logger.info("Generating summary for chunk...")
            chunk_summary = make_openai_client_api_call(messages, model)
            if not chunk_summary:
                message = f"Failed to create summary for chunk: '{chunk[:15] if chunk and len(chunk) > 15 else chunk}...'"
                logger.error(message, exc_info=True)
                raise Exception(message)
            chunk_summaries.append(chunk_summary)

        # Step 3: Combine chunk summaries into one text for final refinement
        combined_summaries = " ".join(chunk_summaries)

        # Step 4: Refine the combined summaries into a concise overall summary
        refinement_prompt = (
            "You are an expert at summarizing information concisely for business users. "
            "Refine the following summaries into one clear, concise, and readable summary: "
            f"{combined_summaries}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": refinement_prompt},
        ]

        try:
            logger.info("Refining overall summary...")
            output = make_openai_client_api_call(messages, model)

        except Exception as e:
            logger.error(f"Error during refinement: {e}", exc_info=True)
            return ""
    else:
        logger.info(
            f"Prompt size is less than number of allowed tokens, "
            f"so creating summary without breaking into chunks."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text},
        ]
        output = make_openai_client_api_call(messages, model)

    running_secs = (dt.datetime.now() - start_time).microseconds
    logger.info(f"Answer generation took {running_secs / 100000:.2f} seconds.")
    return output


def make_openai_client_api_call_stub(messages: List[Dict[str, str]], model: str):
    return "Mock summary for articles."


def make_openai_client_api_call(messages: List[Dict[str, str]], model: str) -> str:
    start_time = dt.datetime.now()

    article_text = messages[0].get("content")
    article_text_preview = (
        article_text[:15] if article_text and len(article_text) > 15 else article_text
    )
    logger.info(
        f"USER PROMPT (preview of article text that is going to be sent to LLM): '{article_text_preview}...'"
    )
    logger.info("Generating LLM response... ")

    if app_settings.DEBUG_MODE:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=app_settings.OPENROUTER_API_KEY,
        )
        response = client.chat.completions.create(model=model, messages=messages)
    else:
        try:
            client = OpenAI(api_key=app_settings.OPENAI_API_KEY)
            model_for_openai = model.split("/")[-1]
            response = client.chat.completions.create(
                model=model_for_openai, messages=messages
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=app_settings.OPENROUTER_API_KEY,
            )
            response = client.chat.completions.create(model=model, messages=messages)

    if response.choices and len(response.choices) > 0:
        output = response.choices[0].message.content
    else:
        service_error = (
            response.model_extra.get("error") if response.model_extra else None
        )
        if service_error:
            error_metadata = service_error.get("metadata")
            logger.error(
                f"{service_error.get('message')}: {service_error.get('code')}. "
                f"{error_metadata.get('provider_name')}: {error_metadata.get('raw')}"
            )

        logger.error(
            "Request to LLM failed: no data will be saved. Continue processing new articles.\n\n"
        )
        return ""

    usage = response.usage
    logger.info(
        f"NUMBER OF TOKENS used per OpenAI API request: {usage.total_tokens}. "
        f"System prompt (+ conversation history): {usage.prompt_tokens}. "
        f"Generated response: {usage.completion_tokens}."
    )
    running_secs = (dt.datetime.now() - start_time).microseconds
    logger.info(f"Answer generation took {running_secs / 100000:.2f} seconds.")
    logger.info(f"\nLLM'S OUTPUT: {output}\n")
    return output


def get_master_summary_file_path():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_dir, "master_summary.txt")


def num_tokens_from_string(text: str, model_name: str) -> int | None:
    """Returns the number of tokens in a text string."""
    num_tokens = None
    try:
        # TODO: add implementation of getting the size more flexibly
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        # encoding = tiktoken.get_encoding(model_name)
        num_tokens = len(encoding.encode(text))
    except Exception as e:
        logger.error(e, exc_info=True)
    return num_tokens


def get_chunk_size(text: str, model_name: str) -> int:
    """
    Returns the chunk_size based number of tokens in a text string.
    Experiment:
        Start with chunks sized at 25–50% of the model's token limit.
        Include an overlap of 10–20% for smooth transitions.
    """
    n_tokens = num_tokens_from_string(text, model_name)
    # if code failed to get number of tokens use default chunk_size = 3000
    # use 50% of the model's token limit as chunk_size
    chunk_size = n_tokens // 2 if n_tokens else 3000
    return chunk_size


def get_today_logs() -> List[str]:
    """Collects all file paths of log files for today."""
    today = dt.datetime.now().date()
    today_logs = []

    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".log"):
            file_date = dt.datetime.fromtimestamp(
                os.path.getmtime(os.path.join(LOG_DIR, filename))
            ).date()
            if file_date == today:
                today_logs.append(os.path.join(LOG_DIR, filename))

    return today_logs


def create_zip_archive(log_files: List[str]) -> str:
    """Creates zip archive with the specified log files."""
    zip_filename = "logs.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for log_file in log_files:
            zipf.write(log_file, os.path.basename(log_file))
    return zip_filename
