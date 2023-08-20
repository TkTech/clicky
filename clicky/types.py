import enum
from dataclasses import dataclass
from typing import Literal, TypedDict


class ServerConfig(TypedDict):
    bot: Literal["slack", "discord"]
    prefix: str
    tokens: dict[str, str] | None


class WhitelistConfig(TypedDict):
    on: str
    type: str
    id: str
    commands: list[str]


class Configuration(TypedDict):
    servers: dict[str, ServerConfig]
    whitelist: list[WhitelistConfig] | None
    #: Maximum time in seconds for a command to run before it's terminated.
    maximum_command_timeout: int | None


@dataclass
class Identity:
    type: str
    id: str


class ReplyType(enum.Enum):
    """
    The type of reply to send back to the user.
    """

    #: Short messages displayed directly in a channel.
    MESSAGE = enum.auto()
    #: Used for long messages like command output that should be sent as
    #: an attachment (if necessary). For example slack has a limit of ~3000
    #: characters per message, so we cannot use it for long-form output.
    ATTACHMENT = enum.auto()
    #: A short message displayed when an error occurred.
    ERROR = enum.auto()
