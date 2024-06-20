import datetime as dt
import os

import requests
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pandas.tseries.offsets import BDay
from transformers import pipeline, AutoTokenizer

from src.config import app_settings


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


def generate_summary_huggingface(article_text: str, prompt: str, use_inference: bool = True) -> str:
    # model = "meta-llama/Llama-2-7b-chat-hf"
    # model = "facebook/bart-large-cnn"
    model = "t5-large"
    # model = "google/long-t5-local-base"
    start_time = dt.datetime.now()

    # using HuggingFace Inference API is faster than downloading a model
    if use_inference:
        content_summary = get_huggingface_response_inference(article_text, prompt, model)
    else:
        response = get_huggingface_response(article_text, prompt, model, task="text-generation")
        content_summary = response[0]["generated_text"]

    print((dt.datetime.now() - start_time))
    print("GENERATED SUMMARY:", content_summary)

    return content_summary


def get_huggingface_response_inference(article_text: str, prompt: str, model: str) -> str:
    api_url = f"https://api-inference.huggingface.co/models/{model}"

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["article"],
        template=prompt + "\n\n{article}\n\nSummary:"
    )

    # Create a prompt using the template
    full_prompt = prompt_template.format(article=article_text)

    # Make the API request
    response = requests.post(api_url, headers=app_settings.HUGGINGFACE_HEADERS, json={"inputs": full_prompt})

    if response.status_code == 200:
        response_json = response.json()[0]
        result = response_json.get("summary_text")
        result = result if result else response_json.get("generated_text")
        summary = result if result else response_json.get("translation_text")
        return summary
    else:
        raise Exception(f"Failed to get summary: {response.status_code} {response.text}")


def get_huggingface_response(article_text: str, prompt: str, model: str, task: str = "summarization", prefix: str = ""):
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


def get_start_date(as_of_date: dt.date):
    cob_date = (as_of_date - BDay(1)).date()
    return cob_date


def get_master_summary_file_path():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_dir, "master_summary.txt")
