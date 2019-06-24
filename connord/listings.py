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
    """Prints iptables to stdout

    :param tables: list of tables like ['filter']
    :param version: '6' or '4' or 'all'
    :returns: True
    """
    iptables.print_iptables(tables, version)
    return True


def list_countries():
    countries.print_countries()


def list_areas():
    areas.print_areas()


def list_features():
    features.print_features()


def list_types():
    types.print_types()


def filter_servers(
    servers_, netflix, countries_, areas_, features_, types_, load_, match, top
):
    """High-level abstraction to filter servers by given filters

    :returns: the filtered servers
    """
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
def list_servers(countries_, areas_, types_, features_, netflix, load_, match, top):
    """
    List servers filtered by one or more arguments

    :param countries_: List of countries
    :param area_: List of areas
    :param types_: List of types
    :param features_: List of features
    :param netflix: If set filter servers optimized for netflix
    :param load_: An integer to filter servers by load.
    :param match: Apply load filter with 'max', 'min' or 'exact' match
    :param top: Show just top count results.
    :returns: True
    """

    servers_ = servers.get_servers()
    servers_ = filter_servers(
        servers_, netflix, countries_, areas_, features_, types_, load_, match, top
    )

    servers.to_string(servers_, stream=True)
