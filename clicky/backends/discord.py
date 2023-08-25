from io import BytesIO

import discord
from discord import Message

from clicky.backends.base import Backend
from clicky.context import MessageContext
from clicky.types import Identity, ReplyType


class DiscordMessageContext(MessageContext):
    def __init__(self, say):
        self.say = say
        self.message: Message | None = None

    async def pre_run(self):
        self.message = await self.say(":hourglass: Running command...")

    async def post_run(self, *, duration):
        if self.message is None:
            return

        await self.message.edit(
            content=(
                f":white_check_mark: Command completed in {duration:.02f}"
                f" seconds."
            )
        )

    async def reply(self, reply_type: ReplyType, message: str):
        match reply_type:
            case ReplyType.MESSAGE:
                await self.say(message)
            case ReplyType.ERROR:
                await self.say(f":warning: {message}")
            case ReplyType.ATTACHMENT:
                with BytesIO(message.encode("utf-8")) as fp:
                    await self.say(file=discord.File(fp, "output.txt"))
            case _:
                raise ValueError(f"Unknown reply type: {reply_type}")


class DiscordBackend(Backend):
    async def run(self):
        intents = discord.Intents.default()
        intents.message_content = True

        client = discord.Client(intents=intents)
        client.event(self.on_message)
        await client.start(self.backend["settings"]["token"])

    async def on_message(self, message: discord.Message):
        if not message.content.startswith(self.backend["prefix"]):
            return

        await self.on_command(
            message.content[len(self.backend["prefix"]) :].strip(),
            [
                Identity("user", str(message.author.id)),
                Identity("channel", str(message.channel.id)),
                Identity("guild", str(message.guild.id)),
            ],
            DiscordMessageContext(message.reply),
        )
