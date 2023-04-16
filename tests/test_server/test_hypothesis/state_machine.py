from __future__ import annotations

import contextlib
import datetime
import environ
from hypothesis.stateful import RuleBasedStateMachine, invariant
import pg_docker
import pytest

from zombie.server import conf, entrypoint, db
from ..utils import FakeDbTime


class RuleBasedStateMachineWithClient(RuleBasedStateMachine):
    database_pool: pg_docker.DatabasePool

    def __init__(self) -> None:
        super().__init__()
        self._exit_stack = contextlib.ExitStack()
        db_config = self._exit_stack.enter_context(self.database_pool.database())

        config = environ.to_config(
            conf.AppConfig,
            {
                "APP_DB_HOST": db_config.host,
                "APP_DB_NAME": db_config.dbname,
                "APP_DB_USER": db_config.user,
                "APP_DB_PORT": db_config.port,
                "APP_DB_PASSWORD": db_config.password,
                "APP_ENV": "test",
            },
        )
        app = entrypoint.create_app(config)
        self.client = app.test_client()
        self.fake_time = FakeDbTime()
        self.fake_time.set_time(datetime.datetime(2023, 4, 15, 12, 0))

    @classmethod
    def set_database_pool(cls, database_pool: pg_docker.DatabasePool) -> None:
        cls.database_pool = database_pool

    @classmethod
    def make_test_case(cls):
        test_case = super().TestCase
        test_case.set_database_pool = cls.set_database_pool
        return pytest.mark.usefixtures("db_pool_unittest")(test_case)

    @invariant()
    def advance_time(self) -> None:
        self.fake_time.tick_time(datetime.timedelta(seconds=1))

    def teardown(self):
        db.connection_pool().closeall()
        self._exit_stack.close()
