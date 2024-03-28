import sys
import enum
from dataclasses import dataclass

if sys.version_info < (3, 11):
    from typing_extensions import TypedDict, NotRequired
else:
    from typing import Literal, TypedDict, NotRequired


class BackendConfig(TypedDict):
    #: The type of backend that should be started.
    backend: Literal["slack", "discord"]
    #: A command prefix the backend should listen for, such as !clicky or
    #: @clicky.
    prefix: str
    #: Backend-specific settings. See the documentation for the selected
    #: backend to see the options here.
    settings: NotRequired[dict[str, str]]


class WhitelistConfig(TypedDict):
    #: The name of the backend instance this rule should apply to.
    on: str
    #: The type of identifier that this rule should apply to, such as a
    #: "channel" or "user".
    type: str
    #: The unique ID for the given type of identifier.
    id: str
    #: A list of regexes that commands must match to be allowed to run.
    #: These are checked _before_ denies. To allow all commands, simply use
    #: ``.*`` as your regex.
    allow: list[str]
    #: An optional list of regexes that commands must _not_ match to be
    #: allowed to run. These are only checked it the command matched an
    #: ``allow`` rule first. Use this to selectively deny flags (such as
    #: ``--force``) or subcommands (such as ``database deleteeverything``)
    deny: NotRequired[list[str]]


class Configuration(TypedDict):
    #: An optional mapping of backends to configure.
    backends: NotRequired[dict[str, BackendConfig]]
    #: An optional whitelist to allow specific Identities to use commands
    #: based off of simple regex matching.
    whitelist: NotRequired[list[WhitelistConfig]]
    #: Maximum time in seconds for a command to run before it's terminated.
    #: Defaults to 5 minutes.
    maximum_command_timeout: NotRequired[int]


@dataclass
class Identity:
    """
    A simple {type, id} pair that represents an identity associated with
    a message.
    """

    #: The type of identity, such as a "channel" or "user".
    type: str
    #: A unique ID for this identifier, such as a user or channel ID.
    id: str


class ReplyType(enum.Enum):
    """
    The type of reply to send back to the user.

    Backends are free to choose how to handle (or ignore) these reply types.
    Errors can be treated as normal messages, or they may have unique styling,
    for example.
    """

    #: Short messages displayed directly in a channel.
    MESSAGE = enum.auto()
    #: Used for long messages like command output that should be sent as
    #: an attachment (if necessary). For example slack has a limit of ~3000
    #: characters per message, so we cannot use it for long-form output.
    ATTACHMENT = enum.auto()
    #: A short message displayed when an error occurred.
    ERROR = enum.auto()
