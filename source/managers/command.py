import collections

import sqlalchemy

import managers.database
from static.static import declarative_meta


class CommandManager(collections.UserDict):
    def __init__(self):
        collections.UserDict.__init__(self)
        self.database_session = DatabaseManager.create_session()
        self.internal_commands = {Command.quit}
        self.database_commands = {}

    #def get_internal_commands(self):
        #self.internal_commands["quit"] = Command.#

    def commit(self):
        self.database_session.commit()

    """
    def rebuild(self):
        database_commands = {
            alias: command for alias,
            command in self.database_commands.items() if command.enabled is True
        }
        merge_commands(self.internal_commands, )

    def merge_commands(dict, out):
        for a, command in dict.items():
            if command.action:
                command.action.reset()
    """


class Command(declarative_meta):
    __tablename__ = "command"

    id_ = sqlalchemy.Column(sqlalchemy.INT, primary_key=True)
    action = sqlalchemy.Column("action", sqlalchemy.TEXT, nullable=False)
    command = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    enabled = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=True)
    sub_only = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=False)
    mod_only = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=False)

    def __init__(self, **options):
        self.id_ = options.get("id", None)
        self.action = options.get("action")
        self.command = options.get("command", None)
        self.description = options.get("description", None)
        self.enabled = options.get("enabled", True)
        self.sub_only = options.get("sub_only", False)
        self.mod_only = options.get("mod_only", False)


Command.quit = Command(id_="quit", command="quit", description="Shut down bot")
