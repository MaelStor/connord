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

"""Manages server features"""

from connord import ConnordError

FEATURES = {
    "ikev2": "IKEv2/IPSec Protocol",
    "openvpn_udp": "UDP",
    "openvpn_tcp": "TCP",
    "socks": "Socks 5",
    "proxy": "HTTP Proxy",
    "pptp": "PPTP",
    "l2tp": "L2TP/IPSec",
    "openvpn_xor_udp": "OpenVPN UDP Obfuscated",
    "openvpn_xor_tcp": "OpenVPN TCP Obfuscated",
    "proxy_cybersec": "HTTP Proxy CyberSec",
    "proxy_ssl": "HTTP Proxy (SSL)",
    "proxy_ssl_cybersec": "HTTP CyberSec Proxy (SSL)",
    "ikev2_v6": "IKEv2/IPSec IPv6",
    "openvpn_udp_v6": "UDPv6",
    "openvpn_tcp_v6": "TCPv6",
    "wireguard_udp": "WireGuard UDP",
    "openvpn_udp_tls_crypt": "UDP TLS encryption",
    "openvpn_tcp_tls_crypt": "TCP TLS encryption",
}


class FeatureError(ConnordError):
    """
    Thrown within this module
    """


def verify_features(features):
    """
    Verify if features are valid.

    :param features: List of features.
    :returns: True if all features are valid or else raises an exception.
    :raises FeatureError: raises a FeatureError if the format of the features
                          were invalid

    """

    if not isinstance(features, list):
        raise FeatureError("Wrong server features: {!s}".format(features))

    wrong_features = []
    for feature in features:
        if feature not in FEATURES.keys():
            wrong_features.append(feature)

    if wrong_features:
        raise FeatureError("Wrong server features: {!s}".format(wrong_features))

    return True


def filter_servers(servers, features=None):
    """
    Filter a list of servers by feature.

    :param servers: List of servers as parsed from nordvpn api in json format
    :param features: List of features to filter the server list. If None or
                     empty the default 'openvpn_udp' is applied.
    :returns: The filtered list
    """

    if features is None or not features:
        features = ["openvpn_udp"]

    verify_features(features)

    filtered_servers = []
    servers = servers.copy()
    for server in servers:
        append = True
        for feature in features:
            if not server["features"][feature]:
                append = False
                break

        if append:
            filtered_servers.append(server)

    return filtered_servers


def to_string():
    """
    Assemble all features as printable string

    :returns: A simple formatted string to use as output on screen
    """

    result = ""
    for feature, description in FEATURES.items():
        result += "{:26}{}\n".format(feature, description)

    return result.rstrip()


def print_features():
    """Prints all possible features"""
    print(to_string())
