import time
import asyncio
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


async def on_command(
    config: Configuration,
    command: str,
    identifiers: list[Identity],
    context: MessageContext,
    clicky_command: str,
):
    start = time.time()
    await context.pre_run()

    # Using clicky to start clicky would not be great.
    args = shlex.split(command)
    if args and args[0].lower() == clicky_command.lower():
        await context.reply(
            ReplyType.ERROR, "Ignoring recursive clicky command."
        )
        return

    run_string = detect_run_string()
    app_string = shlex.split(run_string)

    process = await asyncio.create_subprocess_exec(
        *app_string,
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    communicate = asyncio.ensure_future(process.communicate())
    done, pending = await asyncio.wait_for(
        communicate, timeout=config.get("maximum_command_timeout", 60 * 5)
    )

    if pending and process.returncode is None:
        # If we got here, the process hasn't completed but the wait_for has
        # timed out.
        try:
            process.kill()
        except ProcessLookupError:
            # Task died before we could kill it.
            pass

        await context.reply(ReplyType.ERROR, "Command timed out.")
        # Should we be calling a post_run cleanup here?
        return

    output, err = await communicate
    await context.reply(ReplyType.ATTACHMENT, output.decode("utf-8"))
    await context.post_run(duration=time.time() - start)


def become_clicky(
    *,
    command: str = "clicky",
    help: str = HELP,
    config: Configuration | typing.Callable[[], Configuration],
):
    """
    Wraps a Click-based CLI application, creating a "clicky" command which
    can be used to start a slack bot that exposes the CLI.

    .. code-block:: python
        :linenos:
        :emphasize-lines: 4
        :caption: Example

          import click
          from clicky.frontends.click import become_clicky

          @become_clicky(
              config={
                  "servers": {
                      "my_slack_server": {
                          "bot": "slack",
                          "prefix": "!hello",
                          "tokens": {
                              "app": "<app_token>",
                              "bot": "<bot_token>"
                          }
                      }
                  },
                  "whitelist": [
                      {
                        "on": "my_slack_server",
                        "type": "user",
                        "id": "TkTech",
                        "commands": [".*"]
                      }
                  ]
              }
          )
          @click.command()
          def cli():
              click.echo('Hello, world!')

          if __name__ == '__main__':
              cli()

    """

    def decorator(app: click.Group | click.Command):
        @click.pass_context
        def wrapped_clicky(ctx: click.Context, backend=None, *args, **kwargs):
            import asyncio

            clicky = Clicky(
                command_name=command,
                config=config() if callable(config) else config,
                # PyCharm's type-checker gets confused by partial()
                on_command=partial(on_command, clicky_command=command),  # noqa
            )
            clicky.setup_logging()
            asyncio.run(clicky.run(backend=backend))

        if isinstance(app, click.Group):
            func = app.command(name=command, help=help)(wrapped_clicky)
            click.argument("backend", required=False)(func)
        else:
            new_group = click.Group()
            new_group.add_command(app)
            func = new_group.command(name=command, help=help)(wrapped_clicky)
            click.argument("backend", required=False)(func)
            return new_group

        return app

    return decorator
