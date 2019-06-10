# vim: set fileencoding=utf-8 :

# connord - connect to nordvpn servers
# Copyright (C) 2019  Mael Stor <maelstor@posteo.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sqlite3
from sqlite3 import Error
from cachetools import cached, TTLCache
from connord import ConnordError
from connord import resources


class SqliteError(ConnordError):
    """Thrown within this module"""


def create_connection(db_file=None):
    """Create a database connection"""
    if not db_file:
        db_file = resources.get_database_file()

    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as error:
        print(error)

    return None


def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except Error as error:
        print(error)


def create_location(connection, location):
    sql = """ INSERT OR IGNORE INTO locations(
                latitude,
                longitude,
                display_name,
                city,
                country,
                country_code
              )
              VALUES(?,?,?,?,?,?) """

    try:
        cursor = connection.cursor()
        cursor.execute(sql, location)
        return cursor.lastrowid
    except Error as error:
        print(error)


def location_exists(connection, latitude, longitude):
    sql = """SELECT latitude, longitude FROM locations
            WHERE latitude = {} AND longitude = {}""".format(
        latitude, longitude
    )

    try:
        cursor = connection.cursor()
        result = cursor.execute(sql).fetchone()
        return bool(result)
    except Error as error:
        print(error)


def get_city(connection, latitude, longitude):
    sql = """SELECT city FROM locations
            WHERE latitude = {} AND longitude = {}""".format(
        latitude, longitude
    )

    try:
        cursor = connection.cursor()
        result = cursor.execute(sql).fetchone()
        return result
    except Error as error:
        print(error)


@cached(cache=TTLCache(ttl=60, maxsize=5))
def get_locations(connection):
    connection.row_factory = sqlite3.Row
    sql = """SELECT * FROM locations"""

    try:
        cursor = connection.cursor()
        result = cursor.execute(sql).fetchall()
        return result
    except Error as error:
        print(error)


def get_display_name(connection, latitude, longitude):
    sql = """SELECT display_name FROM locations
            WHERE latitude = {} AND longitude = {}""".format(
        latitude, longitude
    )

    try:
        cursor = connection.cursor()
        result = cursor.execute(sql).fetchone()
        return result
    except Error as error:
        print(error)


def create_location_table(connection):
    sql_create_location_table = """ CREATE TABLE IF NOT EXISTS locations(
                                        latitude text NOT NULL,
                                        longitude text NOT NULL,
                                        display_name text NOT NULL,
                                        city text NOT NULL,
                                        country NOT NULL,
                                        country_code NOT NULL,
                                        UNIQUE(latitude, longitude)
                                    ); """

    if connection:
        create_table(connection, sql_create_location_table)
    else:
        raise SqliteError("Could not create a database connection.")
