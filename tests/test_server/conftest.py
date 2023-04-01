import pytest




@pytest.fixture
def db_connection(configure_db):
    with db.connection() as conn:
        yield conn
