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
"""Manage location database and formatting of areas"""

import time
import requests
from cachetools import cached, LRUCache
import cachetools.func
from connord import ConnordError, Printer
from connord import servers
from connord import sqlite
from connord.formatter import Formatter


class AreaError(ConnordError):
    """Thrown within this module"""


API_URL = "https://nominatim.openstreetmap.org"


@cached(cache=LRUCache(maxsize=50))
def query_location(latitude, longitude):
    """Query location given with latitude and longitude coordinates
    from remote nominatim api. The values are cached to reduce queries.
    The nominatim api restricts queries to 1/sec.


    :param latitude: string with the latitude in float notation
    :param longitude: string with the longitude in float notation
    :returns: dictionary of the response in json
    """
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) "
        "Gecko/20100101 Firefox/60.0"
    }

    endpoint = "reverse"
    flags = {
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "addressdetails": "1",
        "accept-language": "en",
        "zoom": "18",
    }
    url = "{}/{}.php?".format(API_URL, endpoint)
    for k, v in flags.items():
        url += "{}={}&".format(k, v)

    url = url.rstrip("&")
    with requests.get(url, headers=header, timeout=1) as response:
        time.sleep(1)
        return response.json()


def init_database(connection):
    """Initialize location database

    :param connection: a database connection
    """

    with connection:
        sqlite.create_location_table(connection)


def update_database():
    """Updates the location database with least possible online queries."""
    connection = sqlite.create_connection()
    with connection:
        init_database(connection)

    servers_ = servers.get_servers()
    printer = Printer()
    progress_bar = printer.incremental_bar(
        "Updating location database", max=len(servers_)
    )

    for server in servers_:
        longitude = str(server["location"]["long"])
        latitude = str(server["location"]["lat"])

        connection = sqlite.create_connection()
        with connection:
            if sqlite.location_exists(connection, latitude, longitude):
                progress_bar.next()
                continue
            else:
                location_d = query_location(latitude, longitude)

        display_name = location_d["display_name"]
        city_keys = ["city", "town", "village", "residential", "state"]
        for key in city_keys:
            try:
                city = location_d["address"][key]
                break
            except KeyError:
                continue
        else:
            city = "Unknown"

        country = server["country"]
        country_code = server["flag"].lower()
        location = (latitude, longitude, display_name, city, country, country_code)

        connection = sqlite.create_connection()
        with connection:
            sqlite.create_location(connection, location)

        # if not printer.quiet:
        progress_bar.next()

    progress_bar.finish()


def get_server_angulars(server):
    """Return latitude and longitude from server

    :param server: a dictionary describing a server
    :returns: tuple with latitude and longitude
    """
    latitude = str(server["location"]["lat"])
    longitude = str(server["location"]["long"])
    return (latitude, longitude)


def verify_areas(areas_):
    """Verify a list of areas if they can be resolved to valid areas saved in
    the location database. Ambiguous strings resolve to more than one location.

    :param areas_: list of areas
    :returns: list of found areas
    :raises: ValueError if an area could not be found
             AreaError if the area string is ambiguous
    """
    if not isinstance(areas_, list):
        raise TypeError(
            "Expected areas to be <class 'list'>: But found {!s}".format(type(areas_))
        )

    locations = get_locations()
    translation_table = get_translation_table()

    areas_not_found = []
    # side effect: get rid of double entries in areas_ from command-line
    areas_found = {area: list() for area in areas_}
    for area in areas_found.keys():
        for location in locations:
            city = location["city"]
            city_trans = city.translate(translation_table)
            city_lower = city_trans.lower()
            if city_lower.startswith(area):
                areas_found[area].append(city)

        if not areas_found[area]:
            areas_not_found.append(area)

    if areas_not_found:
        raise ValueError("Areas not found: {!s}".format(areas_not_found))

    ambiguous_areas = {}
    for area, cities in areas_found.items():
        if len(cities) > 1:
            ambiguous_areas[area] = cities

    if ambiguous_areas:
        error_string = ""
        for area, cities in ambiguous_areas.items():
            error_string += " {}: {},".format(area, cities)

        error_string = error_string.rstrip(",")
        raise AreaError("Ambiguous Areas:{}".format(error_string))

    return [area for area in areas_found.keys()]


def get_translation_table():
    """Translate special characters to the english equivalent

    :returns: a translation table
    """
    return str.maketrans("áãčëéşșť", "aaceesst")


def filter_servers(servers_, areas_):
    """Filter servers by areas

    :param servers_: list of servers as dictionary
    :param areas_: list of areas as string
    :returns: servers which match the list of areas
    :raises: TypeError when servers_ is None
    """

    if servers_ is None:
        raise TypeError("Servers may not be None")

    if areas_ is None or not areas_ or not servers_:
        return servers_

    translation_table = get_translation_table()
    areas_lower = [str.lower(area) for area in areas_]
    areas_trans = [area.translate(translation_table) for area in areas_lower]

    filtered_servers = []
    connection = sqlite.create_connection()
    with connection:
        for server in servers_:
            lat, lon = get_server_angulars(server)
            if not sqlite.location_exists(connection, lat, lon):
                update_database()

            city = sqlite.get_city(connection, lat, lon)[0]
            city = city.translate(translation_table)
            city = city.lower()
            for area in areas_trans:
                if city.startswith(area):
                    filtered_servers.append(server)
                    break

    return filtered_servers


def get_min_id(city):
    """Calculate the minimum string which must be given to identify an area
    unambiguously

    :param city: the area/city as string
    :returns: the minimum string
    """

    min_id = ""
    translation_table = get_translation_table()
    for char in city:
        char = char.translate(translation_table)
        min_id += char.lower()
        try:
            verify_areas([min_id])
            break
        except AreaError:
            continue

    return min_id


@cachetools.func.ttl_cache(ttl=60, maxsize=1)
def get_locations():
    """Return all locations found in the database. If the database does not exist
    update the database

    :returns: a list of all locations
    """
    connection = sqlite.create_connection()
    with connection:
        locations = sqlite.get_locations(connection)
        if not locations:
            update_database()
            return sqlite.get_locations(connection)

        return locations


class AreasPrettyFormatter(Formatter):
    """Format areas in pretty format"""

    def format_headline(self, sep="="):
        """Format the headline

        :param sep: filling character and separator
        :returns: the headline
        """
        headline = self.format_ruler(sep) + "\n"
        headline += "{:8}: {:^15} {:^15}  {:4}\n".format(
            "Mini ID", "Latitude", "Longitude", "City"
        )
        headline += "{}\n".format("Address")
        headline += self.format_ruler(sep)
        return headline

    def format_area(self, location):
        """Format the area

        :param location: tuple of strings (latitude, longitude)
        :returns: the area as string
        """
        lat = float(location["latitude"])
        lon = float(location["longitude"])
        display_name = location["display_name"]
        city = location["city"]
        min_id = get_min_id(city)

        string = "{!r:8}: {: 14.9f}° {: 14.9f}°  {:40}\n".format(min_id, lat, lon, city)
        string += "{}\n".format(display_name)
        string += self.format_ruler(sep="-")
        return string


def to_string(stream=False):
    """High-level command to format areas and returns the resulting string if not
    streaming directly to screen.

    :param stream: True if the output shall be streamed to stdout
    :returns: When streaming an empty string or else the result of the formatter
    """
    formatter = AreasPrettyFormatter()
    file_ = formatter.get_stream_file(stream)

    locations = get_locations()

    headline = formatter.format_headline()
    print(headline, file=file_)

    for location in locations:
        area = formatter.format_area(location)
        print(area, file=file_)

    return formatter.get_output()


def print_areas():
    """High-level command to print areas to stdout"""
    to_string(stream=True)
