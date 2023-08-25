import logging

from typing import Callable, Awaitable

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
            Awaitable[None],
        ],
    ):
        self.command_name = command_name
        self.config = config
        self.on_command_handler = on_command

    async def run(self, backend: str | None = None):
        # If there are no backends configured, we just don't want to do
        # anything. This is to support say, loading config from a django
        # model and maybe getting no rows without having to do anything
        # special.
        backends = self.config.get("backends", {})
        if not backends:
            return

        if len(backends) > 1 and backend is None:
            # There's ambiguity as to which backend to start.
            raise RuntimeError(
                "There is more than 1 configured backend, but which backend"
                " to start was not specified."
            )
        elif len(backends) == 1:
            backend_config = list(backends.values())[0]
        else:
            try:
                backend_config = backends[backend]
            except KeyError:
                raise RuntimeError(
                    f"No configured backend exists with the name {backend!r},"
                    f" choices are: {list(backends.keys())}."
                )

        match backend_config["backend"]:
            case "slack":
                from clicky.backends.slack import SlackBackend

                backend = SlackBackend(self, backend, backend_config)
                await backend.run()
            case "discord":
                from clicky.backends.discord import DiscordBackend

                backend = DiscordBackend(self, backend, backend_config)
                await backend.run()
            case _:
                raise ValueError(
                    f"Unknown backend type: {backend_config['backend']}"
                )

    async def on_command(
        self, command: str, identifiers: list[Identity], context: MessageContext
    ):
        """
        Called when a command is received from a backend that should be
        forwarded to the frontend for execution.
        """
        await self.on_command_handler(
            self.config, command, identifiers, context
        )

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
