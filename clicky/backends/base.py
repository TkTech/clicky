import re
import abc
import shlex

from clicky.app import Clicky
from clicky.context import MessageContext
from clicky.types import Identity, ReplyType, BackendConfig, WhitelistConfig


class Backend(abc.ABC):
    """
    A :class:`Backend` implements the 3rd-party side of Clicky. These can be
    bots for Slack or Discord, or local options like a GUI wizard or CLI
    wizard like Torgon.
    """

    def __init__(self, app: Clicky, name: str, backend: BackendConfig):
        self.app = app
        self.backend = backend
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

                for allowed_command in entry["allow"]:
                    if not re.match(allowed_command, command):
                        continue

                    # Found a possible match, now lets make sure there's
                    # no explicit rule denying it.
                    for deny in entry.get("deny", []):
                        if re.match(deny, command):
                            # Explicitly denied, but a further identifier
                            # may allow it so just break out of the loop.
                            break
                    else:
                        # If we made it here, either there were no denies or
                        # no deny matched.
                        return True

        return False
