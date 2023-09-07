import datetime as dt

from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pandas.tseries.offsets import BDay


def generate_summary(text: str, prompt: str) -> str:
    full_prompt = f"{prompt}\n{text}"
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    pages = text_splitter.split_text(full_prompt)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.create_documents(pages)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0301")
    chain = load_summarize_chain(llm, chain_type="refine")

    content_summary = chain.run(texts)
    return content_summary


def get_start_date(as_of_date: dt.date):
    cob_date = (as_of_date - BDay(1)).date()
    return cob_date
