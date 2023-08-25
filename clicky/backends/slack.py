import time

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from clicky.backends.base import Backend
from clicky.context import MessageContext
from clicky.types import Identity, ReplyType


class SlackMessageContext(MessageContext):
    def __init__(self, say):
        self.say = say
        self.message_id = None
        self.start_time = None

    async def pre_run(self):
        self.start_time = time.time()
        self.message_id = (
            await self.say(
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
            )
        )["ts"]

    async def reply(self, reply_type: ReplyType, message: str):
        match reply_type:
            case ReplyType.MESSAGE:
                await self.say(message)
            case ReplyType.ERROR:
                await self.say(
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
                await self.say.client.files_upload_v2(
                    channel=self.say.channel,
                    content=message,
                    title="Result of command run.",
                )
            case _:
                raise ValueError(f"Unknown reply type: {reply_type}")

    async def post_run(self, *, duration=None):
        await self.say.client.chat_update(
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
    async def run(self):
        slack_app = AsyncApp(token=self.backend["settings"]["bot_token"])
        slack_app.message(self.backend["prefix"])(self.on_message)
        handler = AsyncSocketModeHandler(
            slack_app, self.backend["settings"]["app_token"]
        )
        await handler.start_async()

    async def on_message(self, message, say):
        if not message["text"].startswith(self.backend["prefix"]):
            return

        await self.on_command(
            message["text"][len(self.backend["prefix"]) :].strip(),
            [
                Identity("user", message["user"]),
                Identity("channel", message["channel"]),
                Identity("team", message["team"]),
            ],
            SlackMessageContext(say),
        )
