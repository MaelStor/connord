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

import time
import requests
from progress.bar import IncrementalBar
from cachetools import cached, LRUCache, TTLCache
from connord import ConnordError
from connord import servers
from connord import sqlite
from connord.formatter import Formatter


class AreaError(ConnordError):
    """Thrown within this module"""


API_URL = "https://nominatim.openstreetmap.org"


@cached(cache=LRUCache(maxsize=50))
def query_location(latitude, longitude):
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
    with connection:
        sqlite.create_location_table(connection)


def update_database():
    connection = sqlite.create_connection()
    with connection:
        init_database(connection)

    servers_ = servers.get_servers()
    for server in IncrementalBar("Updating locations", max=len(servers_)).iter(
        servers_
    ):

        longitude = str(server["location"]["long"])
        latitude = str(server["location"]["lat"])

        connection = sqlite.create_connection()
        with connection:
            if sqlite.location_exists(connection, latitude, longitude):
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


def get_server_angulars(server):
    latitude = str(server["location"]["lat"])
    longitude = str(server["location"]["long"])
    return (latitude, longitude)


def verify_areas(areas_):
    if not isinstance(areas_, list):
        raise AreaError("Wrong areas: {!s}".format(areas_))

    locations = get_locations()

    areas_not_found = []
    # side effect: get rid of double entries in areas_ from command-line
    areas_found = {area: list() for area in areas_}
    for area in areas_found.keys():
        for location in locations:
            city = location["city"]
            city_lower = city.lower()
            if city_lower.startswith(area):
                areas_found[area].append(city)

        if not areas_found[area]:
            areas_not_found.append(area)

    if areas_not_found:
        raise ValueError("Areas not found: {!s}".format(areas_not_found))

    ambigous_areas = {}
    for area, cities in areas_found.items():
        if len(cities) > 1:
            ambigous_areas[area] = cities

    if ambigous_areas:
        error_string = ""
        for area, cities in ambigous_areas.items():
            error_string += " {}: {},".format(area, cities)

        error_string = error_string.rstrip(",")
        raise AreaError("Ambigous Areas:{}".format(error_string))

    return [area for area in areas_found.keys()]


def get_translation_table():
    return str.maketrans("áãčëéşșť", "aaceesst")


def filter_servers(servers_, areas_):
    """Filter servers by areas"""

    if servers_ is None:
        raise TypeError("Servers may not be None")

    if areas_ is None or not areas_ or not servers_:
        return servers_

    areas_lower = [str.lower(area) for area in areas_]
    areas_found = verify_areas(areas_lower)

    filtered_servers = []
    connection = sqlite.create_connection()
    with connection:
        translation_table = get_translation_table()
        for server in servers_:
            lat, lon = get_server_angulars(server)
            if not sqlite.location_exists(connection, lat, lon):
                update_database()

            city = sqlite.get_city(connection, lat, lon)[0]
            city = city.translate(translation_table)
            city = city.lower()
            for area in areas_found:
                if city.startswith(area):
                    filtered_servers.append(server)
                    break

    return filtered_servers


def get_min_id(city):
    min_id = ""
    word = ""
    translation_table = get_translation_table()
    for char in city:
        word += char.lower()
        char = char.translate(translation_table)
        min_id += char.lower()
        try:
            verify_areas([word])
            break
        except AreaError:
            continue
        except ValueError:
            continue

    return min_id


@cached(cache=TTLCache(ttl=60, maxsize=1))
def get_locations():
    connection = sqlite.create_connection()
    with connection:
        locations = sqlite.get_locations(connection)
        if not locations:
            update_database()
            return sqlite.get_locations(connection)

        return locations


class AreasPrettyFormatter(Formatter):
    def format_headline(self, sep="="):
        headline = self.format_ruler(sep) + "\n"
        headline += "{:8}: {:^15} {:^15}  {:40}\n".format(
            "Mini ID", "Latitude", "Longitude", "City"
        )
        headline += "{}\n".format("Address")
        headline += self.format_ruler(sep)
        return headline

    def format_area(self, location):
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
    to_string(stream=True)
