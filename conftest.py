import pytest
from django.db import connection


@pytest.fixture(scope="session", autouse=True)
def enable_pg_trgm(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
