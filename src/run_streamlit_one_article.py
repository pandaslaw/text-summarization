import streamlit as st

from src.database import create_session, CryptonewsArticlesDump


def run(session):
    url = "https://cryptoslate.com/ftx-reorganizing-on-chain-assets-by-bridging-tokens-consolidating-holdings/"
    article = (
        session.query(CryptonewsArticlesDump)
        .filter(CryptonewsArticlesDump.news_url == url)
        .one()
    )

    st.write(
        f"""
    # Original article: 
    ### {url}
    {article.body}   
    # Summary:
    {article.content_summary}
    """
    )


if __name__ == "__main__":
    with create_session() as session:
        run(session)
