# pylint: disable=redefined-outer-name, import-error

import pytest
from connord import sqlite
from main_test_module import get_stub_file


@pytest.fixture(scope="module")
def database():
    return get_stub_file("location_database.sqlite3")


def test_location_exists_when_it_does_not_exist(database):
    conn = sqlite.create_connection(database)
    result = sqlite.location_exists(conn, 0, 0)
    assert not result


def test_location_exists_when_it_does_exist(database):
    conn = sqlite.create_connection(database)
    result = sqlite.location_exists(conn, 50.116667, 8.683333)
    assert result
