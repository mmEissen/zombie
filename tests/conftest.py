import psycopg2
import pytest

from zombie.server import db


pytest_plugins = ["pg_docker"]


def setup_db(pg_params):
    """Add any setup logic for your database in here."""
    connection = psycopg2.connect(**pg_params.connection_kwargs())
    db.init(connection)
    connection.close()


@pytest.fixture(scope="session")
def pg_setup_db():
    return setup_db

