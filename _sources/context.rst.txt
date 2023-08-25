Message Context
===============

When a message is received from a :class:`~clicky.backends.base.Backend` such
as Slack, a `MessageContext` is created which can be used to track state. As an
example, the :class:`~clicky.backends.slack.SlackMessageContext` class
will post a message to slack when a command starts, and update it with total
duration after the command finished.

.. autoclass:: clicky.context.MessageContext
  :members:
