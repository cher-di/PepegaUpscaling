import pytest
import tempfile
import os
import sqlite3
import datetime

from pepegaupscaling.database import Database, create_database
from pepegaupscaling.server import Filters


@pytest.fixture(scope='function')
def database():
    db_file = tempfile.mktemp()
    create_database(db_file)
    yield db_file
    os.remove(db_file)


def test_insert(database):
    db = Database(database)
    filters = list(map(str, Filters))
    date = datetime.datetime.now()
    ip = '127.0.0.1'
    db.insert_request(date, '127.0.0.1', filters)
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, date, ip FROM requests")
        request_id, request_date, request_ip = cursor.fetchone()
        assert request_date == date.isoformat()
        assert request_ip == ip

        cursor.execute("SELECT filter_id FROM used_filters WHERE request_id = ?", (request_id,))
        filters_id = cursor.fetchall()
        request_filters = list()
        for (filter_id,) in filters_id:
            cursor.execute("SELECT filter FROM filters WHERE id = ?", (filter_id,))
            request_filters.append(cursor.fetchone()[0])
        assert set(filters) == set(request_filters)


def test_get_last_30_days(database):
    db = Database(database)
    filters = (Filters.SEPIA.value, Filters.UPSCALE_X2.value)
    ip = '127.0.0.1'
    from_date = datetime.datetime(2021, 10, 29)

    ones = datetime.datetime(2021, 10, 11)
    twice = datetime.datetime(2021, 10, 15)
    dates = [
        twice,
        twice,
        ones,
    ]

    for date in dates:
        db.insert_request(date, ip, filters)

    stat = db.get_last_30_days_stat(from_date)
    assert stat[ones.date().isoformat()] == 1
    assert stat[twice.date().isoformat()] == 2
    for date in stat:
        if date not in (ones.date().isoformat(), twice.date().isoformat()):
            assert stat[date] == 0
