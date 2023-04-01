import contextlib

import psycopg2
import psycopg2.extensions
from os import path
import copy


SQL_DIR = path.join(path.dirname(__file__), "sql")
SCHEMA_FILE = path.join(SQL_DIR, "schema.sql")


_db_config = {}
def set_db_config(config: dict[str, object]) -> None:
    global _db_config
    _db_config = copy.deepcopy(config)


@contextlib.contextmanager
def connection() -> psycopg2.extensions.connection:
    connection_ = psycopg2.connect(**_db_config)
    try:
        yield connection_
    except:
        connection_.rollback()
        raise
    else:
        connection_.commit()
    finally:
        connection_.close()
    


def init() -> None:
    with open(SCHEMA_FILE) as schema_file:
        commands = [command for command in schema_file.read().split(";") if command.strip()]

    with connection() as connection_, connection_.cursor() as cursor:
        try:
            for command in commands:
                cursor.execute(command)
        except psycopg2.Error:
            connection_.rollback()
            raise
        else:
            connection_.commit()

