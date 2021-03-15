import sqlite3
import typing
import datetime

from . import Filters


class Database:
    def __init__(self, filepath: str):
        self._filepath = filepath

    def insert_request(self, date: datetime.datetime, ip: str, filters: typing.Iterable[str]):
        with sqlite3.connect(self._filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO requests (date, ip) VALUES (?, ?)", (date.isoformat(), ip))
            request_id = cursor.lastrowid
            for filter_name in filters:
                cursor.execute("SELECT id FROM filters WHERE filter = ?", (filter_name,))
                filter_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO used_filters (request_id, filter_id) VALUES (?, ?)",
                               (request_id, filter_id))
            cursor.close()

    def _get_select_all_dates(self) -> typing.List[datetime.datetime]:
        with sqlite3.connect(self._filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date FROM requests")
            dates = [datetime.datetime.fromisoformat(date[0]) for date in cursor.fetchall()]
            cursor.close()
        return dates

    def get_last_30_days_stat(self, from_date: datetime.datetime):
        last_30_days = [date for date in self._get_select_all_dates() if from_date - date <= datetime.timedelta(days=30)]
        stat = dict()
        for day in range(30):
            curr_date = from_date - datetime.timedelta(days=day)
            stat[curr_date.date().isoformat()] = 0
        for date in last_30_days:
            stat[date.date().isoformat()] += 1
        return stat


def create_database(filepath: str):
    with sqlite3.connect(filepath) as conn:
        cursor = conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                ip TEXT
            );

            CREATE TABLE filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filter TEXT UNIQUE
            );

            CREATE TABLE used_filters (
                request_id INTEGER,
                filter_id INTEGER,
                FOREIGN KEY (request_id) REFERENCES requests (id)
                ON DELETE CASCADE
                ON UPDATE NO ACTION,
                FOREIGN KEY (filter_id) REFERENCES filters (id)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
            )
            """
        )

        for filter_name in map(str, Filters):
            cursor.execute("INSERT INTO filters (filter) VALUES (?)", (filter_name,))

        cursor.close()
