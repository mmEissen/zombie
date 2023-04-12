import psycopg2.errors
import pytest

import environ
import pg_docker
import psql2py_core

from zombie.server import db, conf


pytest_plugins = ["pg_docker"]


@pytest.fixture(autouse=True)
def testing_config(pg_database):
    return environ.to_config(
        conf.AppConfig,
        {
            "APP_DB_HOST": pg_database.host,
            "APP_DB_NAME": pg_database.dbname,
            "APP_DB_USER": pg_database.user,
            "APP_DB_PORT": pg_database.port,
            "APP_DB_PASSWORD": pg_database.password,
            "APP_ENV": "test",
        }
    )


@pytest.fixture(autouse=True)
def configure_db(testing_config: pg_docker.DatabaseParams):
    db.set_db_config(testing_config.db)
    psql2py_core.set_connection_manager(db.connection)


def setup_db(pg_database: pg_docker.DatabaseParams):
    """Add any setup logic for your database in here."""
    db.set_db_config(
        environ.to_config(
            conf.AppConfig,
            {
                "APP_DB_HOST": pg_database.host,
                "APP_DB_NAME": pg_database.dbname,
                "APP_DB_USER": pg_database.user,
                "APP_DB_PORT": pg_database.port,
                "APP_DB_PASSWORD": pg_database.password,
            }
        ).db
    )
    psql2py_core.set_connection_manager(db.connection)
    try:
        db.init()
    except psycopg2.errors.OperationalError:
        pass


@pytest.fixture(scope="session")
def pg_setup_db():
    return setup_db

