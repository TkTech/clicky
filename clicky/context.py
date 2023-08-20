import abc

from clicky.types import ReplyType


class MessageContext(abc.ABC):
    def pre_run(self):
        pass

    def post_run(self):
        pass

    @abc.abstractmethod
    def reply(self, reply_type: ReplyType, message: str):
        pass
