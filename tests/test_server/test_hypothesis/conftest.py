import pytest

@pytest.fixture(scope="class")
def db_pool_unittest(request, pg_database_pool):
    request.cls.set_database_pool(pg_database_pool)
