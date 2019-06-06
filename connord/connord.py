#!/usr/bin/env python
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

"""Main module for connord"""

import argparse
import sys

# from .connord import update
from connord import update
from connord import version
from connord import listings
from connord import connect
from connord import iptables
from connord import user
from connord import servers
from connord import config


def parse_args(argv):
    """Parse arguments
    :returns: list of args

    """
    description = """
connord is a script/service to connect to nordvpn servers. It manages dns
through resolvconf and the firewall through iptables to keep your connection
safe.
"""
    parser = argparse.ArgumentParser(description=description)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-q", "--quiet", action="store_true", help="Be quiet")
    verbosity.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    command = parser.add_subparsers(dest="command")
    update_cmd = command.add_parser(
        "update", help="Update nordvpn configuration files."
    )
    update_cmd.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force update no matter of configuration.",
    )
    list_cmd = command.add_parser(
        "list", help="Prints all servers if no argument is given."
    )
    list_cmd.add_argument(
        "-c",
        "--country",
        action="append",
        nargs="?",
        help="select a specific country. may be specified multiple times. if \
                one of these arguments has no specifier then all country \
                codes are printed.",
    )
    list_cmd.add_argument(
        "-a",
        "--area",
        action="append",
        nargs="?",
        help="select a specific area.may be specified multiple times. if \
                one of these arguments has no specifier then all areas \
                are printed.",
    )
    list_cmd.add_argument(
        "-f",
        "--feature",
        action="append",
        nargs="?",
        help="select servers with a specific list of features. may be  \
                specified multiple times. if one of these arguments has no \
                specifier then all possible features are printed.",
    )
    list_cmd.add_argument(
        "-t",
        "--type",
        action="append",
        nargs="?",
        help="select servers with a specific type. may be specified multiple \
                times. if one of these arguments has no specifier then all \
                possible types are printed.",
    )
    list_cmd.add_argument(
        "--netflix", action="store_true", help="Select servers configured for netflix."
    )
    list_load_group = list_cmd.add_mutually_exclusive_group()
    list_load_group.add_argument(
        "--max-load", dest="max_load", type=int, help="Filter servers by maximum load."
    )
    list_load_group.add_argument(
        "--min-load", dest="min_load", type=int, help="Filter servers by minimum load."
    )
    list_load_group.add_argument(
        "--load", type=int, help="Filter servers by exact load match."
    )
    list_cmd.add_argument("--top", type=int, help="Show TOP count resulting servers.")
    list_cmd.add_argument(
        "--iptables", action="store_true", help="List all rules in iptables"
    )
    connect_cmd = command.add_parser("connect", help="Connect to a server.")
    server_best = connect_cmd.add_mutually_exclusive_group()
    server_best.add_argument(
        "-s",
        "--server",
        type=str,
        nargs=1,
        help="Connect to a specific server. Arguments -c, -a, -f, -t have no \
        effect.",
    )
    server_best.add_argument(
        "-b",
        "--best",
        action="store_true",
        help="Use best server depending on server load. When multiple servers \
        got the same load use the one with the best ping.",
    )
    connect_cmd.add_argument(
        "-c",
        "--country",
        action="append",
        nargs="?",
        help="Select a specific country. May be specified multiple times.",
    )
    connect_cmd.add_argument(
        "-a",
        "--area",
        action="append",
        nargs="?",
        help="Select a specific area. May be specified multiple times.",
    )
    connect_cmd.add_argument(
        "-f",
        "--feature",
        action="append",
        nargs="?",
        help="Select servers with a specific list of features. May be  \
                specified multiple times.",
    )
    connect_cmd.add_argument(
        "-t",
        "--type",
        action="append",
        nargs="?",
        help="Select servers with a specific type. May be specified multiple \
                times.",
    )
    connect_cmd.add_argument(
        "--netflix", action="store_true", help="Select servers configured for netflix."
    )
    connect_load_group = connect_cmd.add_mutually_exclusive_group()
    connect_load_group.add_argument(
        "--max-load", dest="max_load", type=int, help="Filter servers by maximum load."
    )
    connect_load_group.add_argument(
        "--min-load", dest="min_load", type=int, help="Filter servers by minimum load."
    )
    connect_load_group.add_argument(
        "--load", type=int, help="Filter servers by exact load match."
    )
    connect_cmd.add_argument(
        "-d", "--daemon", action="store_true", help="Start in daemon mode."
    )
    connect_cmd.add_argument(
        "-i",
        "--config",
        type=str,
        nargs="?",
        help="Take config from /path/to/config.{yml|ini}.",
    )
    connect_cmd.add_argument(
        "-o",
        "--openvpn",
        dest="openvpn_options",
        type=str,
        nargs=1,
        help="Options to pass through to openvpn as single string",
    )
    udp_tcp = connect_cmd.add_mutually_exclusive_group()
    udp_tcp.add_argument(
        "--udp", action="store_true", help="Use UDP protocol. This is the default"
    )
    udp_tcp.add_argument(
        "--tcp",
        action="store_true",
        help="Use TCP protocol. Only one of --udp or --tcp may be present.",
    )
    command.add_parser(
        "kill", help="Kill all processes of connord. Useful in daemon mode."
    )
    iptables_cmd = command.add_parser("iptables", help="Wrapper around iptables.")
    iptables_cmd_subparsers = iptables_cmd.add_subparsers(dest="iptables_sub")
    iptables_cmd_subparsers.add_parser("reload", help="Reload iptables")
    iptables_cmd_subparsers.add_parser("flush", help="Flush iptables")
    apply_cmd = iptables_cmd_subparsers.add_parser(
        "apply", help="Apply iptables rules defined in configuration"
    )
    apply_cmd.add_argument(
        "domain", type=str, nargs=1, help="Apply iptables rules with domain"
    )
    udp_tcp = apply_cmd.add_mutually_exclusive_group()
    udp_tcp.add_argument(
        "--udp", action="store_true", help="Use UDP protocol. This is the default"
    )
    udp_tcp.add_argument(
        "--tcp",
        action="store_true",
        help="Use TCP protocol. Only one of --udp or --tcp may be present.",
    )
    command.add_parser("version", help="Show version")

    return parser.parse_args(argv)


def process_list_cmd(args):
    """
    Process arguments when command is 'list'

    :param args: Commandline arguments
    :returns: True if processing was successful
    """

    if args.iptables:
        return listings.list_iptables(["filter"], "4")

    _countries = args.country
    _area = args.area
    _types = args.type
    _features = args.feature
    _netflix = args.netflix
    _top = args.top

    if args.max_load:
        _load = args.max_load
        _match = "max"
    elif args.min_load:
        _load = args.min_load
        _match = "min"
    elif args.load:
        _load = args.load
        _match = "exact"
    else:  # apply defaults
        _load = 10
        _match = "max"

    return listings.main(
        _countries, _area, _types, _features, _netflix, _load, _match, _top
    )


def process_connect_cmd(args):
    """
    Process arguments for connect command
    :param object args: Commandline arguments
    :returns: True if processing was successful
    """

    if args.server:
        _server = args.server
    elif args.best:
        _server = "best"
    else:  # apply default
        _server = "best"

    _countries = args.country
    _areas = args.area
    _features = args.feature
    _types = args.type
    _netflix = args.netflix

    if args.max_load:
        _load = args.max_load
        _match = "max"
    elif args.min_load:
        _load = args.min_load
        _match = "min"
    elif args.load:
        _load = args.load
        _match = "exact"
    else:  # apply defaults
        _load = 10
        _match = "max"

    _daemon = args.daemon
    _config = args.config
    _openvpn = args.openvpn_options

    if args.udp:
        _protocol = "udp"
    elif args.tcp:
        _protocol = "tcp"
    else:  # apply default
        _protocol = "udp"

    return connect.connect(
        _server,
        _countries,
        _areas,
        _features,
        _types,
        _netflix,
        _load,
        _match,
        _daemon,
        _config,
        _openvpn,
        _protocol,
    )


@user.needs_root
def process_iptables_cmd(args):
    if args.iptables_sub == "flush":
        iptables.reset()
    elif args.iptables_sub == "apply":
        iptables.reset()
        if args.tcp:
            _protocol = "tcp"
        else:
            _protocol = "udp"

        domain = args.domain[0]
        _server = servers.get_server_by_domain(domain)
        if iptables.apply_config_dir(_server, _protocol):
            stats_dict = config.get_stats()
            stats_dict["last_server"] = {}
            stats_dict["last_server"]["domain"] = domain
            stats_dict["last_server"]["protocol"] = _protocol
            config.write_stats(stats_dict)
    elif args.iptables_sub == "reload":
        stats_dict = config.get_stats()
        domain = str()
        _protocol = str()
        try:
            domain = stats_dict["last_server"]["domain"]
            _protocol = stats_dict["last_server"]["protocol"]
        except KeyError:
            print("Could not reload iptables. Apply iptables first.")
            return False

        _server = servers.get_server_by_domain(domain)

        iptables.reset()
        iptables.apply_config_dir(_server, _protocol)
    else:
        raise NotImplementedError("Not implemented")

    return True


def main():
    """Entry Point for the program.
    """

    if not sys.argv[1:]:
        sys.argv.extend(["-h"])

    args = parse_args(sys.argv[1:])

    if args.command == "update":
        # Check user is root instead of catching the PermissionError late.
        try:
            update.update(force=args.force)
        except PermissionError:
            print('Permission Denied: You need to run "connord update" as root')
            sys.exit(1)
    elif args.command == "version":
        version.print_version()
    elif args.command == "list":
        process_list_cmd(args)
    elif args.command == "connect":
        process_connect_cmd(args)
    elif args.command == "kill":
        raise NotImplementedError("'kill' is not implemented yet.")
    elif args.command == "iptables":
        process_iptables_cmd(args)
    else:
        raise NotImplementedError("Could not process commandline arguments.")
