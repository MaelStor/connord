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
from connord.formatter import Formatter

__API_URL = "https://api.nordvpn.com/server"
NETFLIX = ["us", "ca", "jp", "gb", "fr", "it"]


class DomainNotFoundError(ConnordError):
    """Raised when a domain is requested but doesn't exist."""

    def __init__(self, domain, message=None):
        if not message:
            message = "Domain not found: {!r}".format(domain)

        super().__init__(message)
        self.domain = domain


class MalformedDomainError(ConnordError):
    """Raised when domain is not in the expected format."""

    def __init__(self, domain, problem, message=None):
        if not message:
            message = "Invalid domain: {!r}: {}".format(domain, problem)

        super().__init__(message)
        self.problem = problem


def get_server_by_domain(domain):
    """Return server specified with domain as string. Queries the nordvpn api.

    :raises: ValueError if the domain can't be found
    """
    servers = get_servers()
    if ".nordvpn.com" in domain:
        fqdn = domain
    else:
        fqdn = domain + ".nordvpn.com"

    for server in servers:
        if server["domain"] == fqdn:
            return server

    raise ValueError("Domain not found: {!r}.".format(domain))


def get_servers_by_domains(domains):
    """Abstraction of get_server_by_domain for a list of domains.

    :returns: list of filtered servers
    :raises: DomainNotFoundError if the domain doesn't exist.
    """
    fqdns = []
    for domain in domains:
        if ".nordvpn.com" in domain:
            fqdn = domain
        else:
            fqdn = domain + ".nordvpn.com"

        fqdns.append(fqdn)

    servers = get_servers()
    filtered_servers = []
    for server in servers:
        for fqdn in fqdns:
            if server["domain"] == fqdn:
                filtered_servers.append(server)
                fqdns.remove(fqdn)
                break

    if not fqdns:
        raise DomainNotFoundError(fqdns[0])

    return filtered_servers


@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_servers():
    """Returns the queried servers from nordvpn's api as list of dictionaries."""
    header = {
        "User-Agent": " ".join(
            (
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0)",
                "Gecko/20100101 Firefox/60.0",
            )
        )
    }

    with requests.get(__API_URL, headers=header, timeout=1) as response:
        return response.json()


def filter_netflix_servers(servers, countries_):
    """Return a list of netflix optimized servers"""
    servers = servers.copy()
    servers = countries.filter_servers(servers, NETFLIX)
    return servers


class ServersPrettyFormatter(Formatter):
    """Class to format servers pretty."""

    def format_headline(self, sep="="):
        """Return formatted headline"""

        headline = self.format_ruler(sep) + "\n"
        headline += "      {:25}  {:6}  {:15}  {:>9}  {}\n".format(
            "Country", "Domain", "IP Address", "Load", "Type"
        )
        headline += "      {}\n".format("Features")
        headline += self.format_ruler(sep)
        return headline

    def format_server(self, server, count, sep="-"):
        """Return pretty formatted server on two lines"""
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

        string = "{:4d}: {:25}  {:6}  {:15}  load: {:>3d}  {}\n".format(
            count, country, ident, ip, load, categories
        )
        string += "      {}\n".format(features)
        string += self.format_ruler(sep)

        return string


def to_string(servers, stream=False):
    """If stream is True stream the formatted servers to stdout else to the
    formatter.output variable.

    :returns: the formatted string if stream is False else ''
    """
    if not servers:
        return str()

    formatter = ServersPrettyFormatter()
    file_ = formatter.get_stream_file(stream)

    headline = formatter.format_headline()
    print(headline, file=file_)
    count = 1
    for server in servers:
        server_s = formatter.format_server(server, count)
        print(server_s, file=file_)
        count += 1

    return formatter.get_output()
