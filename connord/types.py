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

"""Manages server types (categories)"""
# TODO: Rename to categories

from connord import ConnordError
from connord.formatter import Formatter

TYPES = {
    "double": "Double VPN",
    "dedicated": "Dedicated IP",
    "standard": "Standard VPN servers",
    "p2p": "P2P",
    "obfuscated": "Obfuscated Servers",
    "onion": "Onion Over VPN",
}


class ServerTypeError(ConnordError):
    """Throw within this module"""


def verify_types(types):
    """Verify if types is are valid

    :types: a list of types from the command-line
    :raises: ServerTypeError if there are invalid types in types
    :returns: True if all types are valid
    """

    if not isinstance(types, list):
        raise ServerTypeError("Wrong server types: {!s}".format(types))

    wrong_types = []
    for server_type in types:
        if server_type not in TYPES.keys():
            wrong_types.append(server_type)

    if wrong_types:
        raise ServerTypeError("Wrong server types: {!s}".format(wrong_types))

    return True


def verify_types_description(descriptions):
    """Verify if types descriptions are valid

    :description: a list of descriptions
    :raises: ServerTypeError if there are invalid types in types
    :returns: True if all type descriptions are valid
    """

    if not isinstance(descriptions, list):
        raise ServerTypeError("Wrong type: {!s}".format(type(descriptions)))

    wrong_types = [desc for desc in descriptions if desc not in TYPES.values()]

    if wrong_types:
        raise ServerTypeError("Wrong type descriptions: {!s}".format(wrong_types))

    return True


def map_types(types):
    """Map types from command-line to strings used by nordvpn api.

    :types: a list of types from the command-line.
    :returns: a list of mapped types.
    """

    mapped_types = [TYPES[type_] for type_ in types]
    return mapped_types


def map_types_reverse(types):
    """Map types from descriptions to the internal used type codes."""

    verify_types_description(types)
    mapped_types = [
        key for type_ in types for key, value in TYPES.items() if type_ == value
    ]

    return mapped_types


def has_type(server, server_type):
    """Return true if a server has server_type in categories."""
    for category in server["categories"]:
        if category["name"] == server_type:
            return True

    return False


def filter_servers(servers, types=None):
    """Filter a list of servers by type (category).

    :servers: List of servers (parsed from nordvpn api to json).
    :types: List of types (categories). If None or empty the default
            'standard' is applied.
    :returns: The filtered list.
    """

    if types is None or not types:
        types = ["standard"]

    mapped_types = map_types(types)

    filtered_servers = []
    servers = servers.copy()
    for server in servers:
        append = True
        for mapped_type in mapped_types:
            if not has_type(server, mapped_type):
                append = False
                break

        if append:
            filtered_servers.append(server)

    return filtered_servers


class TypesPrettyFormatter(Formatter):
    """Format type in pretty format"""

    def format_headline(self, sep="="):
        """Format headline

        :param sep: the fill character
        :returns: centered string
        """

        types_header = "Server Types"
        return self.center_string(types_header, sep)

    def format_type(self, server_type, description):
        """Format a type

        :param server_type: the type
        :param description: the description
        :returns: the formatted type as string
        """

        return "  {:26}{}".format(server_type, description)


def to_string(stream=False):
    """Gather all types in a printable string

    :param stream: If True print to stdout else print to formatter.output variable
    :returns: Formatted string if stream is False else an empty string
    """
    formatter = TypesPrettyFormatter()
    file_ = formatter.get_stream_file(stream)

    headline = formatter.format_headline()
    print(headline, file=file_)

    for server_type, description in TYPES.items():
        formatted_type = formatter.format_type(server_type, description)
        print(formatted_type, file=file_)

    print(formatter.format_ruler(sep="-"), file=file_)
    return formatter.get_output()


def print_types():
    """Prints all possible types"""
    to_string(stream=True)
