import contextlib

import psycopg2
import psycopg2.extensions
from os import path


SQL_DIR = path.join(path.dirname(__file__), "sql")
SCHEMA_FILE = path.join(SQL_DIR, "schema.sql")


@contextlib.contextmanager
def connection() -> psycopg2.extensions.connection:
    pass


def init(connection: psycopg2.extensions.connection) -> None:
    with open(SCHEMA_FILE) as schema_file:
        commands = schema_file.read().split(";")

    with connection.cursor() as cursor:
        try:
            for command in commands:
                cursor.execute(command)
        except psycopg2.Error:
            connection.rollback()
        else:
            connection.commit()

