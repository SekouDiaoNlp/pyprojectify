"""Console script for pyprojectify."""
import sys
import click

# Typing related imports
from typing import DefaultDict, Dict, List, Optional, Tuple, Union, Generator, Any, Iterator, MutableMapping


@click.command()
def main(args: Optional[str] = None) -> int:
    """Console script for pyprojectify."""
    click.echo("Replace this message by putting your code into "
               "pyprojectify.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
