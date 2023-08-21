Slack
=====

Implements a bot backend for Slack.

Identities
----------

The Slack backend implements the following identities, which can be used to
limit commands to certain users, teams, channels, etc...

.. list-table:: Identities
  :header-rows: 1

  * - Type
    - Example
    - Description
  * - ``user``
    - U012BTV7D5F
    - A unique user ID (**not** a username)
  * - ``channel``
    - N/A
    - A unique channel ID (**not** a name)
  * - ``team``
    - N/A
    - A unique team ID (**not** a name)


API
---

.. autoclass:: clicky.backends.slack.SlackBackend
  :members:

.. autoclass:: clicky.backends.slack.SlackMessageContext
  :members:
