import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from clicky.backends.base import Backend
from clicky.context import MessageContext
from clicky.types import Identity, ReplyType


class SlackMessageContext(MessageContext):
    def __init__(self, say):
        self.say = say
        self.message_id = None
        self.start_time = None

    def pre_run(self):
        self.start_time = time.time()
        self.message_id = self.say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Running command...",
                    },
                }
            ],
            text="Running command...",
        )["ts"]

    def reply(self, reply_type: ReplyType, message: str):
        match reply_type:
            case ReplyType.MESSAGE:
                self.say(message)
            case ReplyType.ERROR:
                self.say(
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f":warning: {message}",
                            },
                        }
                    ],
                    text=message,
                )
            case ReplyType.ATTACHMENT:
                self.say.client.files_upload_v2(
                    channel=self.say.channel,
                    content=message,
                    title="Result of command run.",
                )
            case _:
                raise ValueError(f"Unknown reply type: {reply_type}")

    def post_run(self):
        duration = time.time() - self.start_time

        self.say.client.chat_update(
            channel=self.say.channel,
            ts=self.message_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Command completed in {duration:.02f} seconds.",
                    },
                }
            ],
            text="Command complete.",
        )


class SlackBackend(Backend):
    def run(self):
        slack_app = App(token=self.server["tokens"]["bot"])
        slack_app.message(self.server["prefix"])(self.on_message)
        handler = SocketModeHandler(slack_app, self.server["tokens"]["app"])
        handler.start()

    def on_message(self, message, say):
        if not message["text"].startswith(self.server["prefix"]):
            return

        self.on_command(
            message["text"][len(self.server["prefix"]) :].strip(),
            [
                Identity("user", message["user"]),
                Identity("channel", message["channel"]),
                Identity("team", message["team"]),
            ],
            SlackMessageContext(say),
        )
