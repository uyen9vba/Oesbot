import logging
import datetime

import sqlalchemy

from contextlib import contextmanager

from src.wrappers.helix import HelixManager

Base = sqlalchemy.ext.declarative_base()

class UserAuth(Base):
    def __init__(self, id_, login, name):
        self.id_ = id_
        self.login = login
        self.name = name

    def json(self):
        return {"id": self.id_, "login": self.login, "name": self.name}
    
    def get_by_login(self, login):
        userdata = HelixManager.get_userdata_by_login(login)

        if userdata is None:
            return None

        return UserAuth(userdata["id"], userdata["login"], userdata["display_name"])
        
    def get_by_auth(self, ClientAuth):
        userdata = HelixManager.get_userdata_by_auth(ClientAuth)

        return UserAuth(userdata["id"], userdata["login"], userdata["display_name"])

    def get_userauths_by_id(self, ids):
        userdatas = HelixManager.get_userdatas_by_id(ids)

        return [
            UserAuth(userdata["id"], userdata["login"], userdata["display_name"])
            if userdata is not None
            else None
            for userdata in userdatas
        ]

    def get_userauths_by_login(self, logins):
        userdatas = HelixManager.get_userdatas_by_login(logins)

        return [
            UserAuth(userdata["id"], userdata["login"], userdata["display_name"])
            if userdata is not None
            else None
            for userdata in userdatas
        ]

class User(Base):
    __tablename__ = "user"

    id_ = Column(TEXT, primary_key=True, nullable=False)
    login = Column("login"), TEXT, nullable=False, index=True)
    login_last_updated = Column(UtcDateTime(), nullable=False, server_default="NOW()")
    name = Column(TEXT, nullable=False, index=True)
    subscriber = Column(BOOLEAN, nullable=False, server_default="FALSE")
    moderator = Column(BOOLEAN, nullable=False, server_default="FALSE")
    line_count = Column(BIGINT, nullable=False, server_default="0", index=True)
    last_seen = Column(UtcDateTime(), nullable=True, server_default="NULL")
    last_active = Column(UtcDateTime(), nullable=True, server_default="NULL")
    ignored = Column(BOOLEAN, nullable=False, server_default="FALSE")
    banned = Column(BOOLEAN, nullable=False, server_default="FALSE")
    timeout_end = Column(UtcDateTime(), nullable=True, server_default="NULL")

    def __init__(self, *args, **kwargs):
        self.subscriber = False
        self.moderator = False
        self.line_count = 0
        self.last_seen = None
        self.last_active = None
        self.ignored = False
        self.banned = False
        self.timeout_end = None

    @login.getter
    def login(self):
        return self.login

    @login.setter
    def login(self, login):
        self.login = login
    
    def name(self):
        return self.name

    def line_count(self):
        return self.line_count

    @timeout_end.getter
    def timeout_end(self):
        return self.timeout_end is not None and self.timeout_end > datetime.datetime.utcnow()

    @timeout_end.setter
    def timeout_end(self, timeout_end):
        self.timeout_end = None

    def timeout(self, length, warning_module=None, use_warnings=True):
        message = f"timed out for {length} seconds"

        if use_warnings and warning_module is not None:
            redis = RedisManager.get()
            chances = warning_module.settings["chances"]

            warning_keys = [
                f"warnings:{warning_module.settings["redis_prefix"]}:
                {self.id_}:{warning_id}" for warning_id in range(0, chances)
            ]
            warnings = RedisManager.mget(warning_keys)
            chances_used = len(warnings) - warnings.count(None)

            if chances_used < chances:
                length = warning_module.settings["base_timeout"] * (chances_used + 1)
                message = f"timed out for {length} seconds (warning)"

                for a in range(0, len(warning_keys)):
                    if warnings[a] is None:
                        redis.setex(
                            warning_keys[a],
                            time=warning_module.settings["length"],
                            value=1
                        )

    return (length, message)

    def json(self):
        return {
            "id": self.id_,
            "login": self.login,
            "name": self.name,
            "subscriber": self.subscriber,
            "moderator": self.moderator,
            "line_count": self.line_count,
            "last_seen": self.last_seen.isoformat(),
            "last_active": self.last_active.isoformat(),
            "ignored": self.ignored,
            "banned": self.banned,
            "timeout_end": self.timeout_end.isoformat()
        }

    @staticmethod
    def create(Session, UserAuth):
        user_found = Session.query(User).filter_by(id=UserAuth.id_).one_or_none()
        
        if user_found is not None:
            user_found.login = UserAuth.login
            user_found.name = UserAuth.name

            return user_found
        
        user = User(id=UserAuth.id_, login=UserAuth.login, name=UserAuth.name)
        Session.add(user)
        
        return user

    def query_by_login(Session, login):
        user_found = (
            Session.query(User).filter_by(login=login).order_by(User.login_last_updated.desc()).one_or_none()
        )

        return user_found

    def query_by_id(Session, id):
        return Session.query(User).filter_by(id=id).one_or_none()