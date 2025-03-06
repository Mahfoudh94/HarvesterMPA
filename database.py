from abc import ABC

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine as SqlEngine
from sqlalchemy.orm import DeclarativeBase, Session

import config


class ModelBase(DeclarativeBase):
    pass


class DatabaseEngineFactory(ABC):
    @staticmethod
    def mysql(host, username, password, database) -> SqlEngine:
        engine_string = "mysql+pymysql://" \
            + (username or "") \
            + (':' if username and password else '') \
            + (password or "") \
            + ('@' if username and password else '') \
            + host + (f'/{database}' if database else '')
        return create_engine(engine_string)


conf = config.Config()
HOST = conf.get("Database.Host")
USERNAME = conf.get("Database.Username")
PASSWORD = conf.get("Database.Password")
DATABASE = conf.get("Database.Database")

base_engine = DatabaseEngineFactory.mysql(
    host=HOST,
    username=USERNAME,
    password=PASSWORD,
    database=DATABASE
)

base_session = Session(base_engine)
