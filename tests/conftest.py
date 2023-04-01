import pytest

import psycopg2
import psql2py_core

from zombie.server import db


pytest_plugins = ["pg_docker"]



@pytest.fixture(autouse=True)
def configure_db(pg_database):
    db.set_db_config(pg_database.connection_kwargs())
    psql2py_core.set_connection_manager(db.connection)


def setup_db(pg_database):
    """Add any setup logic for your database in here."""
    db.set_db_config(pg_database.connection_kwargs())
    psql2py_core.set_connection_manager(db.connection)
    db.init()


@pytest.fixture(scope="session")
def pg_setup_db():
    return setup_db

