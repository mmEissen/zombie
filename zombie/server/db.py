import contextlib
import functools

import psycopg2
import psycopg2.extensions
import psycopg2.pool
from os import path
import copy

from zombie.server import conf


SQL_DIR = path.join(path.dirname(__file__), "sql")
SCHEMA_FILE = path.join(SQL_DIR, "schema.sql")


_db_config = {}
_min_pool_size = 1
_max_pool_size = 10
def set_db_config(db_config: conf.AppConfig.DB) -> None:
    global _db_config
    _db_config = {
        "dbname": db_config.name,
        "user": db_config.user,
        "password": db_config.password,
        "host": db_config.host,
        "port": db_config.port,
    }


@functools.lru_cache(maxsize=1)
def connection_pool(key: str) -> psycopg2.pool.AbstractConnectionPool:
    return psycopg2.pool.ThreadedConnectionPool(_min_pool_size, _max_pool_size, **_db_config)


@contextlib.contextmanager
def connection() -> psycopg2.extensions.connection:
    key = f"{_db_config['dbname']}:{_db_config['user']}:{_db_config['password']}:{_db_config['host']}:{_db_config['port']}:{_min_pool_size}:{_max_pool_size}"
    connection_ = connection_pool(key).getconn()
    try:
        yield connection_
    except:
        connection_.rollback()
        raise
    else:
        connection_.commit()
    finally:
        connection_pool(key).putconn(connection_)
    


def init() -> None:
    with open(SCHEMA_FILE) as schema_file:
        schema = schema_file.read()

    with connection() as connection_, connection_.cursor() as cursor:
        try:
            cursor.execute(schema)
        except psycopg2.Error:
            connection_.rollback()
            raise
        else:
            connection_.commit()

