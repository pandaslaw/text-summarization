from logging import getLogger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.config import app_settings
from src.database.models import CryptonewsArticlesDump, Base

logger = getLogger(__name__)


def create_session():
    engine = create_engine(app_settings.DB_CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    return Session()


def run(drop_table: bool = False):
    engine = create_engine(app_settings.DB_CONNECTION_STRING)
    if drop_table:
        CryptonewsArticlesDump.__table__.drop(engine)

    logger.info("Create tables in the database (if they don't exist).")
    Base.metadata.create_all(engine)
    logger.info("Success.")


run(drop_table=False)
