
import psycopg2
import contextlib
import sqlalchemy


class DatabaseManager:
    def __init__(self, url):
        self.engine = sqlalchemy.create_engine(url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine, autoflush=False)
        self.scoped_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bing=self.engine))

    def session(self, **options):
        return self.session(**options)

    def scoped_session(self, **options):
        return self.scoped_session(**options)

    @staticmethod
    def session_add_expunge(self, db_object, **options):
        if "expire_on_commit" not in options:
            options["expire_on_commit"] = False 

        session = self.session(**options)

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
    @contextlib.contextmanager
    def create_dbapi_connection(self, autocommit=False):
        pool_connection = self.engine.raw_connection()

        connection = pool_connection.connection

        try:
            if autocommit:
                if connection.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
                    connection.rollback()

                connection.autocommit = True
            try:
                yield connection
            finally:
                if connection.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
                    connection.rollback()
        finally:
            if autocommit:
                connection.autocommit = False

            pool_connection.close()