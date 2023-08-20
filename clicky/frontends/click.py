import typing
import shlex
import subprocess
from functools import partial

import click

from clicky import Configuration
from clicky.app import Clicky
from clicky.context import MessageContext
from clicky.detect_run_string import detect_run_string
from clicky.types import Identity, ReplyType

HELP = """
Clicky turns your Click-based CLI application into a bot.
"""


def on_command(
    config: Configuration,
    command: str,
    identifiers: list[Identity],
    context: MessageContext,
    clicky_command: str,
):
    # Our first hacky attempt at making this work. We simply fork out to a
    # subprocess to run the command the user is trying to use. This is
    # obviously not ideal, but it's a start. We'll need to do a lot more work
    # to make this work without blocking other commands.
    context.pre_run()

    # Using clicky to start clicky would not be great.
    args = shlex.split(command)
    if args and args[0].lower() == clicky_command.lower():
        context.reply(ReplyType.ERROR, "Ignoring recursive clicky command.")
        return

    run_string = detect_run_string()
    app_string = shlex.split(run_string)

    try:
        # shell=True _must not_ be used here, as it may be used via a shell
        # escape to run arbitrary commands.
        result = subprocess.run(
            [*app_string, *args],
            capture_output=True,
            timeout=config.get("maximum_command_timeout", 5 * 60),
        )
    except subprocess.TimeoutExpired:
        context.reply(ReplyType.ERROR, "Command timed out.")
        return

    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")

    if not len(stdout) and not len(stderr):
        context.reply(ReplyType.ERROR, "Command completed, but had no output.")
    else:
        if stdout:
            context.reply(ReplyType.ATTACHMENT, stdout)
        if stderr:
            context.reply(ReplyType.ATTACHMENT, stderr)

    context.post_run()


def become_clicky(
    *,
    command: str = "clicky",
    help: str = HELP,
    config: Configuration | typing.Callable[[], Configuration],
):
    """
    Wraps a Click-based CLI application, providing a bot interface.
    """

    def decorator(app: click.Group | click.Command):
        @click.pass_context
        def wrapped_clicky(ctx: click.Context, *args, **kwargs):
            Clicky(
                command_name=command,
                config=config() if callable(config) else config,
                # PyCharm's type-checker gets confused by partial()
                on_command=partial(on_command, clicky_command=command),  # noqa
            ).run()

        if isinstance(app, click.Group):
            app.command(name=command, help=help)(wrapped_clicky)
        else:
            new_group = click.Group()
            new_group.add_command(app)
            new_group.command(name=command, help=help)(wrapped_clicky)
            return new_group

        return app

    return decorator
