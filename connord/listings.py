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


def filter_servers_by_count(servers_, top):
    """
    Filter servers to just show top count results

    :param servers_: List of servers
    :param top: Integer to show count servers
    :returns: The filtered servers
    """

    servers_ = servers_.copy()
    filtered_servers = [server for i, server in enumerate(servers_, 1) if i <= top]
    return filtered_servers


def list_iptables(tables, version):
    iptables.print_iptables(tables, version)
    return True


class OverviewPrettyFormatter(Formatter):
    def __init__(self, output=None, max_line_length=80, stream=False):
        super().__init__(output, max_line_length)
        self.stream = stream
        self.has_output = False

    def print_countries(self, countries_):
        if countries_ and None in countries_:
            self.has_output = True
            file_ = self.get_stream_file(self.stream)

            country_header = "Countries"
            print(self.center_string(country_header, sep="="), file=file_)
            for country_code, country in countries.COUNTRIES.items():
                print("  {:6}{}".format(country_code, country), file=file_)
            print(self.format_ruler(sep="-"), file=file_)

    def print_types(self, types_):
        if types_ and None in types_:
            self.has_output = True
            file_ = self.get_stream_file(self.stream)

            types_header = self.center_string("Server Types", sep="=")
            print(types_header, file=file_)
            for server_type, description in types.TYPES.items():
                print("  {:26}{}".format(server_type, description), file=file_)
            print(self.format_ruler(sep="-"), file=file_)

    def print_features(self, features_):
        if features_ and None in features_:
            self.has_output = True
            file_ = self.get_stream_file(self.stream)

            features_header = "Server Features"
            print(self.center_string(features_header, sep="="), file=file_)
            for feature, description in features.FEATURES.items():
                print("  {:26}{}".format(feature, description), file=file_)
            print(self.format_ruler(sep="-"), file=file_)

    def print_areas(self, areas_):
        if areas_ and None in areas_:
            self.has_output = True
            areas.print_areas()


def filter_servers(
    servers_, netflix, countries_, areas_, features_, types_, load_, match, top
):
    servers_ = servers_.copy()
    if load_:
        servers_ = load.filter_servers(servers_, load_, match)
    if netflix:
        servers_ = servers.filter_netflix_servers(servers_, countries_)
    if countries_:
        servers_ = countries.filter_servers(servers_, countries_)
    if areas_:
        servers_ = areas.filter_servers(servers_, areas_)
    if types_:
        servers_ = types.filter_servers(servers_, types_)
    if features_:
        servers_ = features.filter_servers(servers_, features_)
    if top:
        servers_ = filter_servers_by_count(servers_, top)

    return servers_


# TODO: rename to list_servers
def main(countries_, areas_, types_, features_, netflix, load_, match, top):
    """
    Main method to do the actual listing and prints the resulting
    list of servers.

    :param countries_: List of countries
    :param area_: List of areas
    :param types_: List of types
    :param features_: List of features
    :param netflix: If set filter servers optimised for netflix
    :param load_: An integer to filter servers by load.
    :param match: Apply load filter with 'max', 'min' or 'exact' match
    :param top: Show just top count results.
    :returns: True
    """

    formatter = OverviewPrettyFormatter(stream=True)
    formatter.print_countries(countries_)
    formatter.print_areas(areas_)
    formatter.print_types(types_)
    formatter.print_features(features_)

    if not formatter.has_output:
        servers_ = servers.get_servers()
        servers_ = filter_servers(
            servers_,
            netflix,
            countries_,
            areas_,
            features_,
            types_,
            load_,
            match,
            top,
        )

        servers.to_string(servers_, stream=True)

    return True
