Clicky
======

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   identities
   context
   frontends/index
   backends/index
   types


Clicky is a simple Python tool for taking CLIs written using `click`_
and exposing them through :doc:`Backends </backends/index>`, which can be bots
on services like :class:`Slack <clicky.backends.slack.SlackBackend>` and
:class:`Discord <clicky.backends.discord.DiscordBackend>`.

Clicky is inspired-by and borrows some code from `Trogon`_.

Why?
----

Because when you've already invested a bunch of time making a CLI, you don't
want to spend two months making a Slack bot that does the same thing.

Installation
------------

Clicky is available on PyPI:

.. code::

  pip install "clicky[click,slack]"

Usage With Click
----------------

Clicky is designed to be used as a library that can be quickly integrated
into an existing CLI application.

.. code:: python

  import click
  from clicky.frontends.click import become_clicky

  @become_clicky(
      config={
          "backends": {
              "my_slack_server": {
                  "backend": "slack",
                  "prefix": "!hello",
                  "settings": {
                      "app_token": "<app_token>",
                      "bot_token": "<bot_token>"
                  }
              }
          },
          "whitelist": [
              {
                  "on": "my_slack_server",
                  "type": "user",
                  "id": "U012BTV7D5F",
                  "allow": [".*"]
              }
          ]
      }
  )
  @click.command()
  def cli():
      """A simple CLI."""
      click.echo('Hello, world!')

  if __name__ == '__main__':
      cli()

This will expose the `cli` command as a bot on Slack. The bot will respond to
any user on the server using the command '!hello', but only the user with the
ID ``U012BTV7D5F`` will be allowed to run anything.

Config can be provided by a function, in case you want to load it from a file,
populate tokens from a secret store, etc:

.. code:: python

  import json
  import click
  from clicky.frontends.click import become_clicky

  def get_config():
      with open('clicky.json', 'rb') as source:
          return json.load(source)

  @become_clicky(config=get_config)
  @click.command()
  def cli():
      """A simple CLI."""
      click.echo('Hello, world!')

  if __name__ == '__main__':
      cli()

Clicky will add itself as a subcommand to the CLI, so you can run it like this:

.. code::

  $ python my_cli.py clicky

If you added more than one backend, specify which one to start:

.. code::

  $ python my_cli.py clicky my_slack_server

Limitations
-----------

Clicky doesn't currently support any way to handle interactive commands.
As a workaround, we suggest adding support for a ``--yes`` CLI flag or another
way to skip any prompts.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _click: https://click.palletsprojects.com/
.. _Trogon: https://github.com/Textualize/trogon