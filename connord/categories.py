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

"""Manages server categories"""

from connord import ConnordError
from connord.formatter import Formatter

CATEGORIES = {
    "double": "Double VPN",
    "dedicated": "Dedicated IP",
    "standard": "Standard VPN servers",
    "p2p": "P2P",
    "obfuscated": "Obfuscated Servers",
    "onion": "Onion Over VPN",
}


class CategoriesError(ConnordError):
    """Throw within this module"""


def verify_categories(categories):
    """Verify if categories is are valid

    :categories: a list of categories from the command-line
    :raises: CategoriesError if there are invalid categories in categories
    :returns: True if all categories are valid
    """

    if not isinstance(categories, list):
        raise CategoriesError("Wrong server categories: {!s}".format(categories))

    wrong_categories = []
    for server_type in categories:
        if server_type not in CATEGORIES.keys():
            wrong_categories.append(server_type)

    if wrong_categories:
        raise CategoriesError("Wrong server categories: {!s}".format(wrong_categories))

    return True


def verify_categories_description(descriptions):
    """Verify if categories descriptions are valid

    :description: a list of descriptions
    :raises: CategoriesError if there are invalid categories in categories
    :returns: True if all type descriptions are valid
    """

    if not isinstance(descriptions, list):
        raise CategoriesError("Wrong type: {!s}".format(type(descriptions)))

    wrong_categories = [desc for desc in descriptions if desc not in CATEGORIES.values()]

    if wrong_categories:
        raise CategoriesError("Wrong category descriptions: {!s}".format(wrong_categories))

    return True


def map_categories(categories):
    """Map categories from command-line to strings used by nordvpn api.

    :categories: a list of categories from the command-line.
    :returns: a list of mapped categories.
    """

    mapped_categories = [CATEGORIES[category] for category in categories]
    return mapped_categories


def map_categories_reverse(categories):
    """Map categories from descriptions to the internal used type codes."""

    verify_categories_description(categories)
    mapped_categories = [
        key for category in categories for key, value in CATEGORIES.items() if category == value
    ]

    return mapped_categories


def has_category(server, category):
    """Return true if a server has category in categories."""
    for category_ in server["categories"]:
        if category_["name"] == category:
            return True

    return False


def filter_servers(servers, categories=None):
    """Filter a list of servers by type (category).

    :servers: List of servers (parsed from nordvpn api to json).
    :categories: List of categories (categories). If None or empty the default
            'standard' is applied.
    :returns: The filtered list.
    """

    if categories is None or not categories:
        categories = ["standard"]

    mapped_categories = map_categories(categories)

    filtered_servers = []
    servers = servers.copy()
    for server in servers:
        append = True
        for mapped_category in mapped_categories:
            if not has_category(server, mapped_category):
                append = False
                break

        if append:
            filtered_servers.append(server)

    return filtered_servers


class CategoriesPrettyFormatter(Formatter):
    """Format type in pretty format"""

    def format_headline(self, sep="="):
        """Format headline

        :param sep: the fill character
        :returns: centered string
        """

        categories_header = "Categories"
        return self.center_string(categories_header, sep)

    def format_category(self, category, description):
        """Format a category

        :param category: the category
        :param description: the description
        :returns: the formatted category as string
        """

        return "  {:26}{}".format(category, description)


def to_string(stream=False):
    """Gather all categories in a printable string

    :param stream: If True print to stdout else print to formatter.output variable
    :returns: Formatted string if stream is False else an empty string
    """
    formatter = CategoriesPrettyFormatter()
    file_ = formatter.get_stream_file(stream)

    headline = formatter.format_headline()
    print(headline, file=file_)

    for category, description in CATEGORIES.items():
        formatted_category = formatter.format_category(category, description)
        print(formatted_category, file=file_)

    print(formatter.format_ruler(sep="-"), file=file_)
    return formatter.get_output()


def print_categories():
    """Prints all possible categories"""
    to_string(stream=True)
