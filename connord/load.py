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

import abc
from connord import ConnordError


class LoadError(ConnordError):
    """The Error thrown within this module"""


class Filter(metaclass=abc.ABCMeta):
    """
    Abstract class for different filters applied to servers.
    """

    __MAX = 100
    __MIN = 0

    def __init__(self, servers):
        """
        Initialise a Filter
        :param servers: A list of servers

        """
        self.servers = servers

    def __verify_load(self, load):
        """
        Verify if load is valid

        :load: Expects an integer between 0 and 100 inclusive
        :returns: True if load is valid
        :raises LoadError: If load is invalid
        """

        if not isinstance(load, int):
            raise LoadError('Wrong type "{}": {!s}'.format(type(load), load))
        elif load > self.__MAX or load < self.__MIN:
            raise LoadError("Load must be >= 0 and <= 100.")
        else:
            return True

    def apply(self, load):
        """
        Apply filters on servers

        :param load: Expects an integer between 0 and 100 inclusive
        :returns: Filtered list of servers
        """
        servers = self.servers

        if servers is None:
            raise TypeError("Servers may not be None")
        elif load is None or not servers:
            return servers
        else:
            self.__verify_load(load)

        filtered_servers = self.filter_(load)

        return filtered_servers

    @abc.abstractmethod
    def filter_(self, load):
        """
        To be implemented by subclasses
        :param load: Expects an integer between 0 and 100 inclusive
        :returns: A list of filtered servers
        """


class LoadFilter(Filter):
    """
    Filter to match load exactly
    """

    def filter_(self, load):
        filtered_servers = [server for server in self.servers if server["load"] == load]
        return filtered_servers


class MaxLoadFilter(Filter):
    """
    Filter to match maximum load
    """

    def filter_(self, load):
        filtered_servers = [server for server in self.servers if server["load"] <= load]
        return filtered_servers


class MinLoadFilter(Filter):
    """
    Filter to match minimum load
    """

    def filter_(self, load):
        filtered_servers = [server for server in self.servers if server["load"] >= load]
        return filtered_servers


def filter_servers(servers, load, match="max"):
    """
    Filter a list of servers by load.

    :param servers: List of servers.
    :param load: An integer between 0 and 100 inclusive.
    :param match: Match load 'exact', 'max' or 'min'. Default is 'max'.
    :returns: The filtered list.
    :raises ValueError: If value of match is invalid.
    """

    servers = servers.copy()
    if match == "exact":
        return LoadFilter(servers).apply(load)
    elif match == "max":
        return MaxLoadFilter(servers).apply(load)
    elif match == "min":
        return MinLoadFilter(servers).apply(load)
    else:
        raise ValueError('Match must be one of "exact","max" or "min".')
