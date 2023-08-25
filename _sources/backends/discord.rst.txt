Discord
=======

Implements a bot backend for Discord.

Identities
----------

The Discord backend implements the following identities, which can be used to
limit commands to certain users, guilds, channels, etc...

.. list-table:: Identities
  :header-rows: 1

  * - Type
    - Description
  * - ``user``
    - A unique user ID (**not** a username)
  * - ``channel``
    - A unique channel ID (**not** a name)
  * - ``guild``
    - A unique guild ID (**not** a name)


API
---

.. autoclass:: clicky.backends.discord.DiscordBackend
  :members:

.. autoclass:: clicky.backends.discord.DiscordMessageContext
  :members:
