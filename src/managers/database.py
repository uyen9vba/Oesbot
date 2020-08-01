import logging

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from static import globals

logger = logging.getLogger("salbot")

class DatabaseManager:
    n_engine = None
    n_session = None
    n_scoped_session = None

    @staticmethod
    def init(url):
        DatabaseManager.engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20)
        DatabaseManager.n_session = sessionmaker(
            bind=DatabaseManager.n_engine, 
            autoflush=False
        )
        DatabaseManager.n_scoped_session= scoped_session(sessionmaker(bing=DatabaseManager.n_engine))

    @staticmethod
    def create_session(**options):
        return DatabaseManager.n_session(**options)

    @staticmethod
    def create_scoped_session(*options):
        return DatabaseManager.n_scoped_session(**options)

    @staticmethod
    def session_add_expunge(db_object, **options):
        if "expire_on_commit" not in options:
            options["expire_on_commit"] = False 

        session = DatabaseManager.create_session(**options)

        try:
            session.add(db_object)
            session.commit()
            session.expunge(db_object)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    @contextmanager
    def create_dbapi_connection(autocommit=False):
        

