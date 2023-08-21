import re
import abc
import shlex

from clicky.app import Clicky
from clicky.context import MessageContext
from clicky.types import Identity, ReplyType, ServerConfig, WhitelistConfig


class Backend(abc.ABC):
    """
    A backend is a way to run the bot. It can be a Discord bot, a Slack bot,
    whatever.
    """

    def __init__(self, app: Clicky, name: str, server: ServerConfig):
        self.app = app
        self.server = server
        self.name = name

    @abc.abstractmethod
    def run(self):
        """
        Take over the process and start the bot. This will be called only
        after forking the process, so you can do whatever you want here.
        """

    def on_command(
        self, command: str, identifiers: list[Identity], context: MessageContext
    ):
        """
        Called when there's a command to run.

        Performs a permission check before forwarding the command to the
        frontend (such as click) that is responsible for actually running it.
        """
        if not self.is_allowed(command, identifiers):
            context.reply(
                ReplyType.ERROR,
                "You are not allowed to run this command.",
            )
            return

        self.app.on_command(command, identifiers, context)

    def is_allowed(self, command: str, identifiers: list[Identity]) -> bool:
        """
        Given a command and a list of 0 or more :class:`clicky.types.Identity`
        objects, check to see if at least 1 of the passed identities is allowed
        to run this command.

        :returns: True if the command is allowed, otherwise False.
        """
        whitelist: list[WhitelistConfig] = self.app.config.get("whitelist", [])
        for entry in whitelist:
            if entry["on"] != self.name:
                continue

            for identifier in identifiers:
                if entry["type"] != identifier.type:
                    continue

                if entry["id"] != identifier.id:
                    continue

                for allowed_command in entry["commands"]:
                    if re.match(allowed_command, command):
                        return True

        return False
