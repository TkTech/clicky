# Clicky

**NOTE:** This project is _incomplete_. It is not yet ready for day-to-day use.

Clicky is a straightforward Python tool for taking CLIs written using [click][]
and exposing them as bots on Slack & Discord.

Clicky is inspired-by and borrows some code from [Trogon][].

## Installation

Clicky is available on PyPI:

```bash
pip install clicky
```

## Usage

Clicky is designed to be used as a library that can be quickly integrated
into an existing CLI application.

```python
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
            {"on": "my_slack_server", "type": "user", "id": "TkTech", "commands": [".*"]}
        ]
    }
)
@click.command()
def cli():
    """A simple CLI."""
    click.echo('Hello, world!')
    
if __name__ == '__main__':
    cli()
```

## License

Clicky is licensed under the MIT license. See the [LICENSE](LICENSE) file for
more information.

[click]: http://click.pocoo.org/
[trogon]: https://github.com/Textualize/trogon