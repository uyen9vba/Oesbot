import sqlalchemy
import re

from static.static import declarative_meta


class PhraseManager:
    def __init__(self, DatabaseManager):
        self.database_session = DatabaseManager.session(expire_on_commit=False)
        self.phrases = []

    def match_phrase(self, message):
        for a in self.phrases:
            if re.match(message, a):
                return True
            
        return False

    def commit(self):
        self.database_session.commit()


class Phrase(declarative_meta):
    __tablename__ = "phrase"

    id_ = sqlalchemy.Column(sqlalchemy.INT, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False, default="")
    phrase  = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    timeout = sqlalchemy.Column(sqlalchemy.INT, nullable=False, default=300)
    permanent = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=False)
    warning = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=True)
    notify = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=True)
    case_sensitive = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=False)
    enabled = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=True)

    def __init__(self, **options):
        self.id_ = options.get("id_", None)
        self.name = options.get("name", None)
        self.timeout = options.get("timeout", 300)
        self.permanent = options.get("permanent", False)
        self.warning = options.get("warning", True)
        self.notify = options.get("notify", True)
        self.case_sensitive = options.get("case_sensitive", False)
        self.enabled = options.get("enabled", True)
