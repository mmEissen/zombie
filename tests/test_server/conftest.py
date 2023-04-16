import pytest

from zombie.server import db

from .utils import FakeDbTime


@pytest.fixture
def db_connection(configure_db):
    with db.connection() as conn:
        yield conn


@pytest.fixture
def fake_db_time():
    return FakeDbTime()
