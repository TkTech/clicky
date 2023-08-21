Identities
==========

Each ``Backend``, such as Slack, exposes 0-or-more ``Identity`` objects when
processing a command. You can use these with features like the ``whitelist``
in the configuration to only allow certain users to use a command, or to
allow a command to only work in certain channels, as an example.

Each backend exposes different a different set of ``Identity`` objects. Check
their documentation to learn more.


Examples
--------

Lets say we want to limit a command to only a specific user on Slack. We would
add a row to the ``whitelist`` in the configuration that looks like this:

.. code-block:: json
  :caption: Example - User Identity

      "whitelist": [
        {
            "on": "my_slack_server",
            "type": "user",
            "id": "U012BTV7D5F",
            "commands": ["^danger\s?.*"]
        }
    ]

This rule would mean that a Slack user with the ID ``U012BTV7D5F`` would be
able to run a command that starts with "danger".

If instead we have a private channel that only admins are in, we could do:

.. code-block:: json
  :caption: Example - Channel Identity

      "whitelist": [
        {
            "on": "my_slack_server",
            "type": "channel",
            "id": "C293434",
            "commands": ["^danger\s?.*"]
        }
    ]

This rule would mean that a user in the channel with the ID ``C293434`` would
be able to run the ``danger`` command.

For safety, Clicky currently only comes with explicit whitelisting and by
default no user can run anything. If you want to allow any user to run any
command the current best way to do that is to use a wildcard per-channel:


.. code-block:: json
  :caption: Example - Wildcard

      "whitelist": [
        {
            "on": "my_slack_server",
            "type": "channel",
            "id": "C293434",
            "commands": [".*"]
        }
    ]

This would allow any user in the channel to run any command.


If you want to support more complex permission checks, or to pull rules from a
database or other source, you can subclass a backend and replace the
:meth:`~clicky.backends.base.Backend.is_allowed` method.
