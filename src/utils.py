import datetime as dt
import os
import time
from logging import getLogger

import requests
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from pandas.tseries.offsets import BDay
from transformers import pipeline, AutoTokenizer

from src.config import app_settings

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


def generate_summary_huggingface(
    article_text: str, prompt: str, use_inference: bool = True
) -> str:
    # model = "meta-llama/Llama-2-7b-chat-hf"
    # model = "facebook/bart-large-cnn"
    model = "t5-large"
    # model = "google/long-t5-local-base"
    start_time = dt.datetime.now()

    # using HuggingFace Inference API is faster than downloading a model
    if use_inference:
        content_summary = get_huggingface_response_inference(
            article_text, prompt, model
        )
    else:
        response = get_huggingface_response(
            article_text, prompt, model, task="text-generation"
        )
        content_summary = response[0]["generated_text"]

    print((dt.datetime.now() - start_time))
    print("GENERATED SUMMARY:", content_summary)

    return content_summary


def get_huggingface_response_inference(
    article_text: str, prompt: str, model: str
) -> str:
    api_url = f"https://api-inference.huggingface.co/models/{model}"

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["article"], template=prompt + "\n\n{article}\n\nSummary:"
    )

    # Create a prompt using the template
    full_prompt = prompt_template.format(article=article_text)

    # Make the API request
    response = requests.post(
        api_url, headers=app_settings.HUGGINGFACE_HEADERS, json={"inputs": full_prompt}
    )

    counter = 0
    while counter < 10:
        if response.status_code == 200:
            response_json = response.json()[0]
            result = response_json.get("summary_text")
            result = result if result else response_json.get("generated_text")
            summary = result if result else response_json.get("translation_text")
            return summary
        time.sleep(10)
        counter += 1
        print(
            f"Failed to get summary: {response.status_code} {response.text}. Retrying.."
        )
    else:
        raise Exception(
            f"Failed to get summary: {response.status_code} {response.text}"
        )


def get_huggingface_response(
    article_text: str,
    prompt: str,
    model: str,
    task: str = "summarization",
    prefix: str = "",
):
    full_prompt = f"{prompt}\n\n'''{article_text}'''"
    tokenizer = AutoTokenizer.from_pretrained(model)
    if prefix:
        full_prompt = f"{prefix}{full_prompt}"

    hf_pipeline = pipeline(
        task,  # LLM task
        model=model,
        # torch_dtype=torch.float32,
        device_map="auto",
    )
    sequences = hf_pipeline(
        full_prompt,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=1024,
        #         max_new_tokens=200,
    )
    return sequences


def summarize_article(
    article_text: str,
    system_prompt: str,
) -> str:
    """
    Calls LLM using system prompt and article's text message.
    Language model and system prompt are specified in .env configuration file.
    """
    if not article_text:
        logger.info("Article input is empty. SKIPPING")
        return ""

    model = app_settings.LANGUAGE_MODEL

    start_time = dt.datetime.now()

    logger.info(
        f"USER PROMPT (user input, the message that is sent to LLM): '{article_text[:15]}...'"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": article_text},
    ]

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


def get_start_date(as_of_date: dt.date):
    cob_date = (as_of_date - BDay(1)).date()
    return cob_date


def get_master_summary_file_path():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_dir, "master_summary.txt")
