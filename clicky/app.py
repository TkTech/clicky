import multiprocessing
import multiprocessing.connection
from typing import Callable

from clicky import Configuration
from clicky.context import MessageContext
from clicky.types import Identity


class Clicky:
    def __init__(
        self,
        command_name: str,
        config: Configuration,
        on_command: Callable[
            [Configuration, str, list[Identity], MessageContext],
            None,
        ],
    ):
        self.command_name = command_name
        self.config = config
        self.on_command_handler = on_command

    def run(self):
        pool = []

        for name, server in self.config["servers"].items():
            match server["bot"]:
                case "slack":
                    from clicky.backends.slack import SlackBackend

                    pool.append(
                        multiprocessing.Process(
                            target=SlackBackend(
                                self,
                                name,
                                server,
                            ).run()
                        )
                    )
                case _:
                    raise ValueError(f"Unknown bot type: {server['bot']}")

        multiprocessing.connection.wait(p.sentinel for p in pool)

    def on_command(
        self, command: str, identifiers: list[Identity], context: MessageContext
    ):
        """
        Called when a command is received from a backend that should be
        forwarded to the frontend for execution.
        """
        self.on_command_handler(self.config, command, identifiers, context)
