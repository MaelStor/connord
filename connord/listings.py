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

"""List servers"""

from connord import servers
from connord import countries
from connord import types
from connord import features
from connord import load
from connord import iptables
from connord import areas
from connord.formatter import Formatter


def filter_servers_by_count(_servers, _top):
    """
    Filter servers to just show _top count results

    :param _servers: List of servers
    :param _top: Integer to show count servers
    :returns: The filtered servers
    """

    _servers = _servers.copy()
    filtered_servers = [server for i, server in enumerate(_servers, 1) if i <= _top]
    return filtered_servers


def list_iptables(tables, version):
    iptables.print_iptables(tables, version)
    return True


class OverviewPrettyFormatter(Formatter):
    def __init__(self, output=None, max_line_length=80, stream=False):
        super().__init__(output, max_line_length)
        self.stream = stream
        self.has_output = False

    def print_countries(self, _countries):
        if _countries and None in _countries:
            self.has_output = True
            _file = self.get_stream_file(self.stream)

            country_header = "Countries"
            print(self.center_string(country_header, sep="="), file=_file)
            for country_code, country in countries.COUNTRIES.items():
                print("  {:6}{}".format(country_code, country), file=_file)
            print(self.format_ruler(sep="-"), file=_file)

    def print_types(self, _types):
        if _types and None in _types:
            self.has_output = True
            _file = self.get_stream_file(self.stream)

            types_header = self.center_string("Server Types", sep="=")
            print(types_header, file=_file)
            for server_type, description in types.TYPES.items():
                print("  {:26}{}".format(server_type, description), file=_file)
            print(self.format_ruler(sep="-"), file=_file)

    def print_features(self, _features):
        if _features and None in _features:
            self.has_output = True
            _file = self.get_stream_file(self.stream)

            features_header = "Server Features"
            print(self.center_string(features_header, sep="="), file=_file)
            for feature, description in features.FEATURES.items():
                print("  {:26}{}".format(feature, description), file=_file)
            print(self.format_ruler(sep="-"), file=_file)

    def print_areas(self, _areas):
        if _areas and None in _areas:
            self.has_output = True
            areas.print_areas()


def filter_servers(
    _servers, _netflix, _countries, _areas, _features, _types, _load, _match, _top
):
    _servers = _servers.copy()
    if _load:
        _servers = load.filter_servers(_servers, _load, _match)
    if _netflix:
        _servers = servers.filter_netflix_servers(_servers, _countries)
    if _countries:
        _servers = countries.filter_servers(_servers, _countries)
    if _areas:
        _servers = areas.filter_servers(_servers, _areas)
    if _types:
        _servers = types.filter_servers(_servers, _types)
    if _features:
        _servers = features.filter_servers(_servers, _features)
    if _top:
        _servers = filter_servers_by_count(_servers, _top)

    return _servers


# TODO: rename to list_servers
def main(_countries, _areas, _types, _features, _netflix, _load, _match, _top):
    """
    Main method to do the actual listing and prints the resulting
    list of servers.

    :param _countries: List of countries
    :param _area: List of areas
    :param _types: List of types
    :param _features: List of features
    :param _netflix: If set filter servers optimised for netflix
    :param _load: An integer to filter servers by load.
    :param _match: Apply load filter with 'max', 'min' or 'exact' match
    :param _top: Show just _top count results.
    :returns: True
    """

    formatter = OverviewPrettyFormatter(stream=True)
    formatter.print_countries(_countries)
    formatter.print_areas(_areas)
    formatter.print_types(_types)
    formatter.print_features(_features)

    if not formatter.has_output:
        _servers = servers.get_servers()
        _servers = filter_servers(
            _servers,
            _netflix,
            _countries,
            _areas,
            _features,
            _types,
            _load,
            _match,
            _top,
        )

        servers.to_string(_servers, stream=True)

    return True
