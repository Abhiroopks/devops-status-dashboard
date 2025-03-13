"""
Manage a Flask-SQLAlchemy application.

This script defines a Flask CLI group, which is a set of commands that can be
executed from the command line using the `flask` command.
The available commands are:

*   ``create_db``: Create the database tables.

"""

from flask.cli import FlaskGroup
from project import db

cli: FlaskGroup = FlaskGroup()


@cli.command("create_db")
def create_db() -> None:
    """
    Create the database tables.

    This command creates the database tables based on the models defined in the
    application.

    """
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    cli()
