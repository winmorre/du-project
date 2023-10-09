from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from configs.settings import get_settings

_settings = get_settings()

# DATABASE_URI = 'postgresql://postgres:<password>@localhost/<name_of_the_datbase>'

def db_url(user, password) -> str:
    return "postgresql://{user}:{password}@mysqlserver/db".format(user=user, password=password)


def get_engine_and_session_local(url: str):
    e = create_engine(
        url, connect_args={}
    )
    return e, sessionmaker(autocommit=False, autoflush=False, bind=e)


Base = declarative_base()


def get_db(user=None, password=None):
    url = db_url(user=user or _settings.mysql_user, password=password or _settings.mysql_password)
    engine, SessionLocal = get_engine_and_session_local(url=url)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["Base", "get_db"]
