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

"""Wrapper around iptables"""

import sys
import os
import re
import netaddr
from iptc import Table, Table6
import iptc
import yaml

from jinja2 import Environment, FileSystemLoader

from connord import ConnordError
from connord import user
from connord import config
from connord.formatter import Formatter


class IptablesError(ConnordError):
    """Raise within this module"""


def get_table_name(config_file):
    table_regex = re.compile(r"[0-9]*[-]?([a-zA-Z]+[6]?).rules")
    base = os.path.basename(config_file)
    result = table_regex.search(base)
    if result:
        return result.group(1)

    filename = os.path.basename(config_file)
    raise IptablesError(
        "Error: {} is not a valid filename for a .rules file.".format(filename))


@user.needs_root
def init_table(table_name):
    if table_name.endswith("6"):
        table_name = table_name[:-1]
        for table in Table6.ALL:
            if table_name == table:
                return Table6(table_name)

        raise TypeError("Error: '{}' is not a valid table.".format(table_name))

    for table in Table.ALL:
        if table_name == table:
            return Table(table)

    raise TypeError("Error: '{}' is not a valid table.".format(table_name))


@user.needs_root
def init_table_from_file_name(config_file):
    table_name = get_table_name(config_file)
    return init_table(table_name)


def is_table_v6(table):
    return isinstance(table, Table6)


def flush_tables(ipv6=False):
    iptc.easy.flush_all(ipv6=ipv6)
    policy = iptc.Policy("ACCEPT")
    for table_s in iptc.easy.get_tables(ipv6):
        for chain_s in iptc.easy.get_chains(table_s, ipv6):
            iptc.easy.set_policy(table_s, chain_s, policy=policy, ipv6=ipv6)


def reset():
    flush_tables()
    flush_tables(ipv6=True)


@user.needs_root
def apply_config(_server, _protocol, config_file):
    table = init_table_from_file_name(config_file)
    table_s = table.name
    is_ipv6 = is_table_v6(table)
    iptc.easy.flush_table(table_s, ipv6=is_ipv6)
    policy = iptc.Policy("ACCEPT")
    for chain_s in iptc.easy.get_chains(table_s, ipv6=is_ipv6):
        iptc.easy.set_policy(table_s, chain_s, policy=policy, ipv6=is_ipv6)

    config_d = read_config(_server, _protocol, config_file)

    for chain_s in config_d:
        if not iptc.easy.has_chain(table_s, chain_s, ipv6=is_ipv6):
            iptc.easy.add_chain(table_s, chain_s, ipv6=is_ipv6)

        if config_d[chain_s]["policy"] != "None":
            policy = iptc.Policy(config_d[chain_s]["policy"])
            iptc.easy.set_policy(table_s, chain_s, policy=policy, ipv6=is_ipv6)
        for rule_d in config_d[chain_s]["rules"]:
            if iptc.easy.test_rule(rule_d, ipv6=is_ipv6):
                try:
                    iptc.easy.add_rule(table_s, chain_s, rule_d, ipv6=is_ipv6)
                except ValueError:
                    raise IptablesError("Malformed rule: {}".format(rule_d))
            else:
                raise IptablesError("Malformed rule: {}".format(rule_d))

    return True


@user.needs_root
def apply_config_dir(_server, _protocol):
    config_files = config.list_config_dir(filetype="rules")
    retval = True
    for config_file in config_files:
        if not apply_config(_server, _protocol, config_file):
            retval = False

    return retval


@user.needs_root
def apply_default_config(_server, _protocol):
    retval = True
    config_files = config.list_config_dir(filetype="fallback")
    for config_file in config_files:
        if not apply_config(_server, _protocol, config_file):
            retval = False

    return retval


def render_template(_server, _protocol, config_file):
    config_data_file = config.get_config_file()
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(config_data_file)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    with open(config_data_file, "r") as config_data:
        config_data_dict = yaml.safe_load(config_data)
        config_data_dict["vpn_remote"] = _server["ip_address"]
        config_data_dict["vpn_protocol"] = _protocol
        if _protocol == "udp":
            config_data_dict["vpn_port"] = "1194"
        elif _protocol == "tcp":
            config_data_dict["vpn_port"] = "443"
        else:
            raise TypeError("Unknown protocol '{}'.".format(_protocol))

        template = env.get_template(os.path.basename(config_file))
        return template.render(config_data_dict)


@user.needs_root
def read_config(_server, _protocol, config_file):
    rendered_template = render_template(_server, _protocol, config_file)
    return yaml.safe_load(rendered_template)


class IptablesPrettyFormatter(Formatter):
    """Pretty format for iptables"""

    def format_table_header(self, table, sep="="):
        prefix = sep * 2
        string = table.name.upper()
        suffix = sep * (self.max_line_length - 4 - len(string))

        table_header = "{} {} {}".format(prefix, string, suffix)
        return table_header

    def format_chain_header(self, chain, sep="="):
        policy = chain.get_policy()
        if policy:
            policy_s = policy.name
        else:
            policy_s = 'None'

        string = "{} ({:^6})".format(chain.name, policy_s)
        return self.center_string(string, sep)

    def format_rule(self, rule, rule_number, sep="-"):
        # convert to short cidr notation
        src_net = str(netaddr.IPNetwork(str(rule.src)).cidr)
        dst_net = str(netaddr.IPNetwork(str(rule.dst)).cidr)

        parameters = rule.target.get_all_parameters()
        if parameters:
            parameters_s = str(parameters)
        else:
            parameters_s = ""

        output = "{:3}: {!s:11} {!s:11} {:6} {!s:18} {!s:18} {:<6}{!s}\n".format(
            rule_number,
            rule.in_interface,
            rule.out_interface,
            rule.protocol,
            src_net,
            dst_net,
            rule.target.name,
            parameters_s,
        )

        if rule.matches:
            matches = ""
            for match in rule.matches:
                matches += "{}{!s},".format(match.name, match.parameters)

            output += "     Matches: {}".format(matches.rstrip(","))

        output += "\n"
        output += self.format_ruler(sep)
        return output


@user.needs_root
def to_string(tables=None, version="4", stream=False):
    if tables is None:
        tables = ["filter"]

    if "filter" in tables and len(tables) == 1:
        if version == "4":
            table = Table(Table.FILTER)
        else:
            raise NotImplementedError(
                "Not implemented yet version '{}'".format(version)
            )
    else:
        raise NotImplementedError("Not implemented yet '{}'".format(str(tables)))

    formatter = IptablesPrettyFormatter()
    if not stream:
        stream = formatter
    else:
        stream = sys.stdout

    table_header = formatter.format_table_header(table)
    print(table_header, file=stream)
    for chain in table.chains:
        chain_header = formatter.format_chain_header(chain)
        print(chain_header, file=stream)
        counter = 1
        for rule in chain.rules:
            rule_s = formatter.format_rule(rule, counter)
            print(rule_s, file=stream)
            counter += 1

    return formatter.get_output()


def print_iptables(tables=None, version="4"):
    to_string(tables, version, stream=True)
