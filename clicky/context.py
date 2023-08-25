import abc

from clicky.types import ReplyType


class MessageContext(abc.ABC):
    async def pre_run(self):
        """
        Called before a command is executed.
        """

    async def post_run(self, *, duration: float):
        """
        Called after a command has finished executing.
        """

    @abc.abstractmethod
    async def reply(self, reply_type: ReplyType, message: str):
        """
        Called whenever the command wants to return data to the user.
        """
