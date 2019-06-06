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


def filter_servers_by_count(_servers, _top):
    """
    Filter servers to just show _top count results

    :param _servers: List of servers
    :param _top: Integer to show count servers
    :returns: The filtered servers
    """

    filtered_servers = [server for i, server in enumerate(_servers, 1) if i <= _top]
    return filtered_servers


def list_iptables(tables, version):
    iptables.print_iptables(tables, version)
    return True


# TODO: rename to list_servers
def main(_countries, _area, _types, _features, _netflix, _load, _match, _top):
    """
    Main method to do the actual listing and prints the resulting
    list of servers.

    :param _countries: List of countries
    :param _area: List of areas
    :param _types: List of types
    :param _features: List of features
    :param _netflix: If set filter servers optimized for netflix
    :param _load: An integer to filter servers by load.
    :param _match: Apply load filter with 'max', 'min' or 'exact' match
    :param _top: Show just _top count results.
    :returns: True
    """

    output = ""
    if _countries and None in _countries:
        output += countries.to_string() + "\n"
    if _area:
        raise NotImplementedError("Area filter is not implemented yet.")
    if _types and None in _types:
        output += types.to_string() + "\n"
    if _features and None in _features:
        output += features.to_string() + "\n"

    if output:
        print(output.rstrip())
    else:
        _servers = servers.get_servers()
        if _netflix:
            if _countries is None:
                _countries = servers.NETFLIX
            else:
                _countries.extend(servers.NETFLIX)
        if _load:
            _servers = load.filter_servers(_servers, _load, _match)
        if _countries:
            _servers = countries.filter_servers(_servers, _countries)
        if _types:
            _servers = types.filter_servers(_servers, _types)
        if _features:
            _servers = features.filter_servers(_servers, _features)
        # keep this the last filter
        if _top:
            _servers = filter_servers_by_count(_servers, _top)

        output += servers.to_string(_servers)

        if output:
            print(output)

    return True
