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

import requests
from cachetools import cached, TTLCache
from connord import ConnordError
from connord.types import map_types_reverse
from connord import countries

__API_URL = "https://api.nordvpn.com/server"
NETFLIX = ["us", "ca", "jp", "gb", "fr", "it"]


class ServerError(ConnordError):
    """Thrown within this module"""


def get_server_by_domain(domain):
    servers = get_servers()
    for server in servers:
        if server["domain"] == domain + ".nordvpn.com":
            return server

    return None


def get_servers_by_domains(servers, domains):
    filtered_servers = [get_server_by_domain(servers, domain) for domain in domains]

    return filtered_servers


@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_servers():
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) \
Gecko/20100101 Firefox/60.0"
    }

    with requests.get(__API_URL, headers=header) as response:
        return response.json()


def filter_netflix_servers(servers, _countries):
    if _countries is None:
        _countries = NETFLIX
    else:
        _countries.extend(NETFLIX)

    servers = countries.filter_servers(servers, _countries)
    return servers


# TODO: May be moved to listings
def to_string(servers):
    if not servers:
        return str()

    sep_sign = "-"
    sep = 6 * " " + 75 * sep_sign + "\n"
    header = "      {:25}  {:6}  {:15}  {:>9}  {}\n".format(
        "Country", "Domain", "IP Address", "Load", "Type"
    )

    header += "      {}\n".format("Features")
    header += sep

    string = str()
    count = 1
    for server in servers:
        ident, _, _ = server["domain"].split(".")
        country = server["country"]
        ip = server["ip_address"]
        load = server["load"]

        categories = [category["name"] for category in server["categories"]]
        categories = ",".join(map_types_reverse(categories))

        features = [
            feature for feature in server["features"] if server["features"][feature]
        ]
        features = ",".join(features)

        string += "{:4d}: {:25}  {:6}  {:15}  load: {:>3d}  {}\n".format(
            count, country, ident, ip, load, categories
        )
        string += "      {}\n".format(features)

        string += sep
        count += 1

    if string:
        string = header + string

    return string.rstrip()
