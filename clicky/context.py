import abc

from clicky.types import ReplyType


class MessageContext(abc.ABC):
    def pre_run(self):
        """
        Called before a command is executed.
        """

    def post_run(self):
        """
        Called after a command has finished executing.
        """

    @abc.abstractmethod
    def reply(self, reply_type: ReplyType, message: str):
        """
        Called whenever the command wants to return data to the user.
        """
