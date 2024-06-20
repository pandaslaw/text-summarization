import datetime as dt
import os

from langchain import HuggingFaceHub, LLMChain, PromptTemplate
from langchain.chains import StuffDocumentsChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.schema import HumanMessage
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pandas.tseries.offsets import BDay
from transformers import pipeline, AutoTokenizer

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

def generate_summary_huggingface(text: str, prompt: str) -> str:
    full_prompt = f"{prompt}\n\n'''{text}'''"
    model = "meta-llama/Llama-2-7b-chat-hf"
    start_time = dt.datetime.now()
    content_summary = get_huggingface_response(model, prompt=full_prompt, task="text-generation")
    print((dt.datetime.now() - start_time))
    print("GENERATED SUMMARY:", content_summary)

    return content_summary[0]["generated_text"]


def get_huggingface_response(model, prompt: str, task: str = "summarization", prefix: str = "") -> None:
    tokenizer = AutoTokenizer.from_pretrained(model)
    if prefix:
        prompt = f"{prefix}{prompt}"

    hf_pipeline = pipeline(
        task,  # LLM task
        model=model,
        # torch_dtype=torch.float32,
        device_map="auto",
    )
    sequences = hf_pipeline(
        prompt,
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
