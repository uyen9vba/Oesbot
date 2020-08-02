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
    engine = None
    session = None
    scoped_session = None

    @staticmethod
    def init(url):
        DatabaseManager.engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20)
        DatabaseManager.session = sessionmaker(
            bind=DatabaseManager.engine, 
            autoflush=False
        )
        DatabaseManager.scoped_session= scoped_session(sessionmaker(bing=DatabaseManager.engine))

    @staticmethod
    def create_session(**options):
        return DatabaseManager.session(**options)

    @staticmethod
    def create_scoped_session(*options):
        return DatabaseManager.scoped_session(**options)

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
        pool_connection = DatabaseManager.engine.raw_connection()

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
