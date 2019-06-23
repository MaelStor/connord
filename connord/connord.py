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
import re

from requests.exceptions import RequestException

from connord import update
from connord import version
from connord import listings
from connord import connect
from connord import iptables
from connord import user
from connord import servers
from connord import resources
from connord import areas
from connord import countries
from connord import features
from connord import types
from .features import FeatureError


# pylint: disable=too-few-public-methods
class DomainType:

    pattern = re.compile(r"(?P<country_code>[a-z]{2})(?P<number>[0-9]+)(.netflix.com)?")

    def __call__(self, value):
        match = self.pattern.match(value)
        if not match:
            raise argparse.ArgumentTypeError(
                "'{}' is not a valid domain. Expected format is"
                " {{country_code}}{{number}}[.netflix.com]".format(value)
            )

        country_code = match.groupdict()["country_code"]
        CountryType().__call__(country_code)
        return value


class CountryType:
    def __call__(self, value):
        try:
            countries.verify_countries([value])
        except countries.CountryError:
            raise argparse.ArgumentTypeError(
                "'{}' is an unrecognized country.".format(value)
            )
        return value


class AreaType:
    def __call__(self, value):
        try:
            areas.verify_areas([value])
        except (areas.AreaError, ValueError) as error:
            raise argparse.ArgumentTypeError(str(error))

        return value


class TypeType:
    def __call__(self, value):
        try:
            types.verify_types([value])
        except types.ServerTypeError:
            raise argparse.ArgumentTypeError(
                "'{}' is an unrecognized type.".format(value)
            )

        return value


class FeatureType:
    def __call__(self, value):
        try:
            features.verify_features([value])
        except FeatureError:
            raise argparse.ArgumentTypeError(
                "'{}' is an unrecognized feature.".format(value)
            )

        return value


class LoadType:
    def __call__(self, value):
        try:
            int_value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "'{}' must be an integer between 0 and 100.".format(value)
            )

        if int_value < 0 or int_value > 100:
            raise argparse.ArgumentTypeError(
                "'{}' must be a value between 0 and 100.".format(value)
            )

        return int_value


class TopType:
    def __call__(self, value):
        try:
            int_value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "'{}' must be a positive integer greater than 0.".format(value)
            )

        if int_value <= 0:
            raise argparse.ArgumentTypeError(
                "'{}' must be a positive integer greater than 0.".format(value)
            )


class TableType:
    def __call__(self, value):
        if iptables.verify_table(value):
            return value

        raise argparse.ArgumentTypeError(
            "'{}' is not a valid table name. Consult man iptables for details.".format(
                value
            )
        )


# pylint: disable=too-many-statements,too-many-locals
def parse_args(argv):
    """Parse arguments

    :returns: list of args
    """
    description = """
Connect to NordVPN servers secure and fast.
DNS is managed with resolvconf and the firewall through iptables to keep
your connection safe.
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
        type=CountryType(),
        help="select a specific country. may be specified multiple times. if"
        " one of these arguments has no specifier then all country"
        " codes are printed.",
    )
    list_cmd.add_argument(
        "-a",
        "--area",
        action="append",
        nargs="?",
        type=AreaType(),
        help="select a specific area.may be specified multiple times. if"
        " one of these arguments has no specifier then all areas"
        " are printed.",
    )
    list_cmd.add_argument(
        "-f",
        "--feature",
        action="append",
        nargs="?",
        type=FeatureType(),
        help="select servers with a specific list of features. may be"
        " specified multiple times. if one of these arguments has no"
        " specifier then all possible features are printed.",
    )
    list_cmd.add_argument(
        "-t",
        "--type",
        action="append",
        nargs="?",
        type=TypeType(),
        help="select servers with a specific type. may be specified multiple"
        " times. if one of these arguments has no specifier then all"
        " possible types are printed.",
    )
    list_cmd.add_argument(
        "--netflix", action="store_true", help="Select servers configured for netflix."
    )
    list_load_group = list_cmd.add_mutually_exclusive_group()
    list_load_group.add_argument(
        "--max-load",
        dest="max_load",
        type=LoadType(),
        help="Filter servers by maximum load.",
    )
    list_load_group.add_argument(
        "--min-load",
        dest="min_load",
        type=LoadType(),
        help="Filter servers by minimum load.",
    )
    list_load_group.add_argument(
        "--load", type=LoadType(), help="Filter servers by exact load match."
    )
    list_cmd.add_argument(
        "--top", type=TopType(), help="Show TOP count resulting servers."
    )
    list_cmd_sub = list_cmd.add_subparsers(dest="list_sub")
    list_ipt_cmd = list_cmd_sub.add_parser(
        "iptables", help="Per default list rules in filter table of ipv4."
    )
    list_ipt_cmd.add_argument(
        "-4", dest="v4", action="store_true", help="(Default) List ipv4 rules"
    )
    list_ipt_cmd.add_argument(
        "-6", dest="v6", action="store_true", help="List ipv6 rules"
    )
    list_all_table = list_ipt_cmd.add_mutually_exclusive_group()
    list_all_table.add_argument(
        "-t",
        "--table",
        type=TableType(),
        action="append",
        help="List TABLE. May be specified multiple times.",
    )
    list_all_table.add_argument(
        "-a", "--all", action="store_true", help="List all tables."
    )
    connect_cmd = command.add_parser("connect", help="Connect to a server.")
    server_best = connect_cmd.add_mutually_exclusive_group()
    server_best.add_argument(
        "-s",
        "--server",
        type=DomainType(),
        nargs=1,
        help="Connect to a specific server. Arguments -c, -a, -f, -t have no"
        " effect.",
    )
    server_best.add_argument(
        "-b",
        "--best",
        action="store_true",
        help="Use best server depending on server load. When multiple servers"
        " got the same load use the one with the best ping.",
    )
    connect_cmd.add_argument(
        "-c",
        "--country",
        action="append",
        nargs="?",
        type=CountryType(),
        help="Select a specific country. May be specified multiple times.",
    )
    connect_cmd.add_argument(
        "-a",
        "--area",
        action="append",
        type=AreaType(),
        nargs="?",
        help="Select a specific area. May be specified multiple times.",
    )
    connect_cmd.add_argument(
        "-f",
        "--feature",
        action="append",
        nargs="?",
        type=FeatureType(),
        help="Select servers with a specific list of features. May be"
        " specified multiple times.",
    )
    connect_cmd.add_argument(
        "-t",
        "--type",
        action="append",
        nargs="?",
        type=TypeType(),
        help="Select servers with a specific type. May be specified multiple" " times.",
    )
    connect_cmd.add_argument(
        "--netflix", action="store_true", help="Select servers configured for netflix."
    )
    connect_load_group = connect_cmd.add_mutually_exclusive_group()
    connect_load_group.add_argument(
        "--max-load",
        dest="max_load",
        type=LoadType(),
        help="Filter servers by maximum load.",
    )
    connect_load_group.add_argument(
        "--min-load",
        dest="min_load",
        type=LoadType(),
        help="Filter servers by minimum load.",
    )
    connect_load_group.add_argument(
        "--load", type=LoadType(), help="Filter servers by exact load match."
    )
    connect_cmd.add_argument(
        "-d", "--daemon", action="store_true", help="Start in daemon mode."
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
    kill_cmd = command.add_parser(
        "kill", help="Kill openvpn processes. Useful in daemon mode."
    )
    kill_cmd.add_argument(
        "-a", "--all", action="store_true", help="Kill all openvpn processes."
    )
    iptables_cmd = command.add_parser("iptables", help="Wrapper around iptables.")
    iptables_cmd_subparsers = iptables_cmd.add_subparsers(dest="iptables_sub")
    iptables_cmd_subparsers.add_parser("reload", help="Reload iptables")
    flush_cmd = iptables_cmd_subparsers.add_parser("flush", help="Flush iptables")
    flush_cmd.add_argument(
        "--no-fallback",
        dest="no_fallback",
        action="store_true",
        help="Flush tables ignoring fallback files",
    )
    apply_cmd = iptables_cmd_subparsers.add_parser(
        "apply", help="Apply iptables rules defined in configuration"
    )
    apply_cmd.add_argument(
        "domain", type=DomainType(), nargs=1, help="Apply iptables rules with domain"
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

    :param args: Command-line arguments
    :returns: True if processing was successful
    """

    if args.list_sub == "iptables":
        if args.v4 and args.v6:
            version_ = "all"
        elif args.v4:
            version_ = "4"
        elif args.v6:
            version_ = "6"
        else:
            version_ = "4"

        if args.all:
            tables = None
        elif args.table:
            tables = args.table
        else:
            tables = ["filter"]

        return listings.list_iptables(tables, version_)

    countries_ = args.country
    area_ = args.area
    types_ = args.type
    features_ = args.feature
    netflix = args.netflix
    top = args.top

    if args.max_load:
        load_ = args.max_load
        match = "max"
    elif args.min_load:
        load_ = args.min_load
        match = "min"
    elif args.load:
        load_ = args.load
        match = "exact"
    else:  # apply defaults
        load_ = 100
        match = "max"

    return listings.main(
        countries_, area_, types_, features_, netflix, load_, match, top
    )


def process_connect_cmd(args):
    """
    Process arguments for connect command

    :param object args: Command-line arguments
    :returns: True if processing was successful
    """

    if args.server:
        server = args.server
    elif args.best:
        server = "best"
    else:  # apply default
        server = "best"

    countries_ = args.country
    areas_ = args.area
    features_ = args.feature
    types_ = args.type
    netflix = args.netflix

    if args.max_load:
        load_ = args.max_load
        match = "max"
    elif args.min_load:
        load_ = args.min_load
        match = "min"
    elif args.load:
        load_ = args.load
        match = "exact"
    else:  # apply defaults
        load_ = 10
        match = "max"

    daemon = args.daemon
    if args.openvpn_options:
        openvpn = args.openvpn_options[0]
    else:
        openvpn = args.openvpn_options

    if args.udp:
        protocol = "udp"
    elif args.tcp:
        protocol = "tcp"
    else:  # apply default
        protocol = "udp"

    return connect.connect(
        server,
        countries_,
        areas_,
        features_,
        types_,
        netflix,
        load_,
        match,
        daemon,
        openvpn,
        protocol,
    )


@user.needs_root
def process_iptables_cmd(args):
    """Process 'iptables' command

    :param object args: command-line arguments as Namespace
    :returns: True if processing was successful
    """

    if args.iptables_sub == "flush":
        if args.no_fallback:
            iptables.reset(fallback=False)
        else:
            iptables.reset(fallback=True)

    # TODO: rearrange apply to apply a specific set of rules like filter.rules
    elif args.iptables_sub == "apply":
        iptables.reset(fallback=True)
        if args.tcp:
            protocol = "tcp"
        else:
            protocol = "udp"

        domain = args.domain[0]
        server = servers.get_server_by_domain(domain)
        # TODO: which action to take when applying rules fails?
        iptables.apply_config_dir(server, protocol)
    elif args.iptables_sub == "reload":
        stats_dict = resources.get_stats()
        domain = str()
        protocol = str()
        try:
            domain = stats_dict["last_server"]["domain"]
            protocol = stats_dict["last_server"]["protocol"]
        except KeyError:
            print("Could not reload iptables. Run 'connect' or apply iptables first.")
            return False

        server = resources.get_stats(stats_name="server")

        iptables.reset(fallback=True)
        iptables.apply_config_dir(server, protocol)
    else:
        raise NotImplementedError("Not implemented")

    return True


@user.needs_root
def process_kill_cmd(args):
    """Process 'kill' command

    :param object args: Namespace object holding the command-line arguments
    """

    if args.all:
        connect.kill_openvpn()
    else:
        ovpn_pid = resources.read_pid()
        connect.kill_openvpn(ovpn_pid)


# This function has a high complexity score but it's kept simple though
# pylint: disable=too-many-branches
def main():  # noqa: C901
    """Entry Point for the program. A first level argument processing method.
    All Exceptions that lead to an exit of the program are catched here.

    :raises: SystemExit either 0 or 1
    """

    if not sys.argv[1:]:
        sys.argv.extend(["-h"])

    args = parse_args(sys.argv[1:])
    try:
        if args.command == "update":
            update.update(force=args.force)
        elif args.command == "version":
            version.print_version()
        elif args.command == "list":
            process_list_cmd(args)
        elif args.command == "connect":
            process_connect_cmd(args)
        elif args.command == "kill":
            process_kill_cmd(args)
        elif args.command == "iptables":
            process_iptables_cmd(args)
        else:
            raise NotImplementedError("Could not process commandline arguments.")
        sys.exit(0)
    except PermissionError:
        print(
            'Permission Denied: You need to run "connord {}" as root'.format(
                args.command
            ),
            file=sys.stderr,
        )
    except resources.ResourceNotFoundError as error:
        print(error)
    except resources.MalformedResourceError as error:
        print(error)
    except areas.AreaError as error:
        print(error)
    except iptables.IptablesError as error:
        print(error)
    except countries.CountryError as error:
        print(error)
    except FeatureError as error:
        print(error)
    except servers.DomainNotFoundError as error:
        print(error)
    except servers.MalformedDomainError as error:
        print(error)
    except connect.ConnectError as error:
        print(error)
    except RequestException as error:
        print(error)

    sys.exit(1)
