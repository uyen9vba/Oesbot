import logging

from psycopg2.extensions import STATUS_IN_TRANSACTION
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from static import globals

logger = logging.getLogger("salbot")

class DatabaseManager:
    @staticmethod
    def __init__(url):
        self.engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20)
        self.session = sessionmaker(
            bind=self.engine, 
            autoflush=False
        )
        self.scoped_session= scoped_session(sessionmaker(bing=self.engine))

    @staticmethod
    def create_session(**options):
        return self.session(**options)

    @staticmethod
    def create_scoped_session(*options):
        return self.scoped_session(**options)

    @staticmethod
    def session_add_expunge(db_object, **options):
        if "expire_on_commit" not in options:
            options["expire_on_commit"] = False 

        session = self.create_session(**options)

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
        pool_connection = self.engine.raw_connection()

        connection = pool_connection.connection

        try:
            if autocommit:
                if connection.status == STATUS_IN_TRANSACTION:
                    connection.rollback()

                connection.autocommit = True
            try:
                yield connection
            finally:
                if connection.status == STATUS_IN_TRANSACTION:
                    connection.rollback()
        finally:
            if autocommit:
                connection.autocommit = False

            pool_connection.close()
