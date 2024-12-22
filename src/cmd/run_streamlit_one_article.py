import streamlit as st

from src.database.connection import create_session


def run(session):
    url = "https://cryptoslate.com/ftx-reorganizing-on-chain-assets-by-bridging-tokens-consolidating-holdings/"
    # article = (
    #     session.query(CryptonewsArticlesDump)
    #     .filter(CryptonewsArticlesDump.news_url == url)
    #     .one()
    # )
    # st.write(
    #     f"""
    # # Original article:
    # ### {url}
    # {article.body}
    # # Summary:
    # {article.content_summary}
    # """
    # )

    st.write(
        f"""
    # Original article: 
    ### {url}
    
    # FTX reorganizing on-chain assets by bridging tokens, consolidating holdings
        Bankrupt crypto exchange FTX revealed in a tweet on Sept. 6 that it is in the process of moving its cryptocurrency holdings.
    
    The company said that it is moving bridged tokens on multiple networks to their native blockchains. FTX has yet to disclose the specific cryptocurrencies affected by this initiative, as well as the exact amount being transferred.
    
    FTX added that it is migrating Solana (SOL) to BitGo, its qualified cryptocurrency custodian. FTX formerly maintained a close relationship with Solana, and the two parties formed mutual investments and partnerships prior to FTX’s collapse.
    
    The exact value of FTX’s crypto holdings remains uncertain. Reports from April suggested that FTX had recovered $7.3 billion of cash and crypto but provided no distinction between the two. Arkham Intelligence, which provides data on FTX’s known addresses, suggests that the company has at least $384 million of crypto including 1,169 SOL ($23,860).
    
    FTX’s latest statement may partially confirm reports from Sept. 2. Those reports suggested that the company moved $10 million in SOL and other Solana-based altcoins to Ethereum via the Wormhole Bridge in a matter of days.
    
    Consolidating assets
    Though FTX did not provide any reason for the latest transfers, its movements seem to be part of its ongoing attempts to consolidate assets. After FTX gathers its funds, it could redeem assets, compensate customers, and possibly relaunch its exchange.
    
    The latest transfers are not the company’s only attempts to move and gather funds.  On Aug. 24, the company filed to have Galaxy Digital manage sales of cryptocurrency on a recurring basis. Additionally, reports from March suggest that FTX transferred about $100 million of dollars worth of stablecoins to exchanges.
    
    While FTX has not officially confirmed all of its transfers, it has been more transparent about non-crypto transactions. The company sold its stake in Mysten Labs, sold its LedgerX acquisition, and initiated a now-paused sale of Anthropic AI shares stake in 2023.
    
    # Summary:
    
    **Executive Summary:**  
    FTX, a bankrupt crypto exchange, has announced that it is in the process of moving its cryptocurrency holdings, including bridged tokens on multiple networks, to their native blockchains. They are also migrating Solana (SOL) to BitGo, their qualified cryptocurrency custodian. FTX's exact crypto holdings remain uncertain, but reports suggest they hold at least $384 million in crypto. This move appears to be part of FTX's ongoing efforts to consolidate assets and possibly relaunch its exchange.
    
    **Conclusion: Bearish Signal**  
    The article presents a bearish signal for FTX. The exchange's bankruptcy and the need to move its crypto holdings indicate financial instability. While they are taking steps to consolidate assets and compensate customers, the lack of transparency regarding the exact holdings and the uncertain future of the exchange create an atmosphere of uncertainty and mistrust in the market. Additionally, their previous close relationship with Solana, which ended with FTX's collapse, adds further skepticism to the situation.
    """
    )


if __name__ == "__main__":
    with create_session() as session:
        run(session)
