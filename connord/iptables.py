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

import os
import re
import netaddr
from iptc import Table, Table6
import iptc
import yaml

from jinja2 import Environment, FileSystemLoader

import netifaces
from connord import ConnordError, Printer
from connord import user
from connord import resources
from connord.formatter import Formatter


class IptablesError(ConnordError):
    """Raise within this module"""


def get_config_path(table, fallback=False, ipv6=False):
    """Return rules path of the table"""
    if fallback:
        if ipv6:
            table_regex = re.compile(r"[0-9]*[-]?{}6.fallback".format(table))
        else:
            table_regex = re.compile(r"[0-9]*[-]?{}.fallback".format(table))

        file_list = resources.list_config_dir(filetype="fallback")
    else:
        if ipv6:
            table_regex = re.compile(r"[0-9]*[-]?{}6.rules".format(table))
        else:
            table_regex = re.compile(r"[0-9]*[-]?{}.rules".format(table))

        file_list = resources.list_config_dir(filetype="rules")

    configs_found = []
    for file_ in file_list:
        result = table_regex.search(file_)
        if result:
            configs_found.append(file_)

    if not configs_found:
        if fallback:
            error_message = (
                "Could not find a fallback configuration for '{}' " "table."
            ).format(table)
        else:
            error_message = "Could not find a configuration for '{}' table.".format(
                table
            )
        raise resources.ResourceNotFoundError(table, error_message)

    elif len(configs_found) > 1:
        raise IptablesError("Ambiguous file paths: {}.".format(configs_found))

    return configs_found[0]


def get_table_name(config_file):
    """Return the table name extracted from the filename"""
    table_regex = re.compile(r"[0-9]*[-]?([a-zA-Z]+[6]?).(rules|fallback)")
    base = os.path.basename(config_file)
    result = table_regex.search(base)
    if result:
        return result.group(1)

    filename = os.path.basename(config_file)
    raise IptablesError(
        "Error: {} is not a valid filename for an iptables rules file.".format(filename)
    )


@user.needs_root
def init_table(table_name):
    """Return a table object with table_name if present in iptc.Table[6].ALL else
    raise a TypeError."""
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
    """Returns a table object with table name extracted from config_file"""
    table_name = get_table_name(config_file)
    return init_table(table_name)


def is_table_v6(table):
    """Return true if the table is ivp6"""
    return isinstance(table, Table6)


def verify_table(table):
    """Return true if the table is a valid table name

    :param table: table as string
    """

    return table in Table.ALL or table in Table6.ALL


def flush_tables(ipv6=False):
    """Flush all tables and apply the default policy ACCEPT to standard tables"""
    printer = Printer()
    with printer.Do("Flushing all tables: ipv6={!r}".format(ipv6)):
        iptc.easy.flush_all(ipv6=ipv6)

    with printer.Do("Setting ACCEPT policy in all chains"):
        policy = iptc.Policy("ACCEPT")
        for table_s in iptc.easy.get_tables(ipv6):
            for chain_s in iptc.easy.get_chains(table_s, ipv6):
                iptc.easy.set_policy(table_s, chain_s, policy=policy, ipv6=ipv6)


def reset(fallback=True):
    """Reset all tables to fallback if True else just flush them"""
    flush_tables()
    flush_tables(ipv6=True)
    if fallback:
        apply_config_dir(filetype="fallback")


def _apply_config(table, config_d, ipv6):
    for chain_s in config_d:
        if not iptc.easy.has_chain(table, chain_s, ipv6=ipv6):
            iptc.easy.add_chain(table, chain_s, ipv6=ipv6)

        try:
            if config_d[chain_s]["policy"] != "None":
                policy = iptc.Policy(config_d[chain_s]["policy"])
                iptc.easy.set_policy(table, chain_s, policy=policy, ipv6=ipv6)
        except KeyError:
            pass

        try:
            for rule_d in config_d[chain_s]["rules"]:
                if iptc.easy.test_rule(rule_d, ipv6=ipv6):
                    try:
                        iptc.easy.add_rule(table, chain_s, rule_d, ipv6=ipv6)
                    except ValueError:
                        raise IptablesError(
                            "Malformed rule: {}\n  in {}.{}".format(
                                rule_d, table, chain_s
                            )
                        )
                else:
                    raise IptablesError(
                        "Malformed rule: {}\n  in {}.{}".format(rule_d, table, chain_s)
                    )
        except KeyError:
            pass


@user.needs_root
def apply_config(config_file, server=None, protocol=None):
    """Apply a configuration to ip[6]tables (depends on the file name)

    :raises: IptablesError if an invalid rule is present. This leaves the
             table intact with rules applied so far.
    """
    table = init_table_from_file_name(config_file)
    table_s = table.name
    is_ipv6 = is_table_v6(table)

    printer = Printer()
    with printer.Do("Flushing table '{}', ipv6={!r}".format(table_s, is_ipv6)):
        iptc.easy.flush_table(table_s, ipv6=is_ipv6)
        policy = iptc.Policy("ACCEPT")
        for chain_s in iptc.easy.get_chains(table_s, ipv6=is_ipv6):
            iptc.easy.set_policy(table_s, chain_s, policy=policy, ipv6=is_ipv6)

    config_base = os.path.basename(config_file)
    with printer.Do("Applying '{}'".format(config_base)):
        config_d = read_config(config_file, server, protocol)
        _apply_config(table_s, config_d, ipv6=is_ipv6)

    return True


@user.needs_root
def apply_config_dir(server=None, protocol=None, filetype="rules"):
    """High-level command to apply the whole configuration directory with rules or
    fallback files in it.

    :param server: If None this applies 0.0.0.0/0 instead
    :param protocol: If None the default 'udp' is taken
    :param filetype: default is rules but may be fallback too.
    :returns: True on success
    """
    config_files = resources.list_config_dir(filetype=filetype)
    retval = True
    for config_file in config_files:
        if not apply_config(config_file, server, protocol):
            retval = False

    return retval


@user.needs_root
def merge_environment(config_data_dict=None):
    """Merge environment files with the configuration file

    Configuration file variables overwrite variables from environment
    """
    env_dict = dict()

    files = resources.list_stats_dir(filetype="env")
    for file_ in files:
        with open(file_, "r") as file_fd:
            yaml_dict = yaml.safe_load(file_fd)
            env_dict.update(yaml_dict)

    if config_data_dict:
        env_dict.update(config_data_dict)

    return env_dict


def get_default_gateway(ipv6=False):
    """Returns a tuple with ipaddress and interface of the default gateway.

    :param ipv6: If true return ip6 address and interface else ip4 address
    :raises IptablesError: If there is no default gateway.
    :returns: a tuple with (ip_address, interface) on success or (None, None) on failure
    """
    try:
        default_gateway = netifaces.gateways()["default"]
    except KeyError:
        raise IptablesError("Could not find a default gateway. Are you connected?")

    if ipv6:
        try:
            gateway = default_gateway[netifaces.AF_INET6]
            return gateway
        except KeyError:
            return (None, None)

    try:
        gateway = default_gateway[netifaces.AF_INET]
        return gateway
    except KeyError:
        return (None, None)


def get_interface_addresses(iface):
    """Returns the iface addresses as dictionary of the given interface."""
    iface_addresses = netifaces.ifaddresses(iface)

    default_iface_dict = {"link": iface_addresses[netifaces.AF_LINK]}
    try:
        default_iface_dict["inet"] = iface_addresses[netifaces.AF_INET]
    except KeyError:
        pass

    try:
        default_iface_dict["inet6"] = iface_addresses[netifaces.AF_INET6]
    except KeyError:
        pass

    return default_iface_dict


def render_template(config_file, server=None, protocol=None):
    """Render a jinja2 template with data from config.yml per default. Adds some
    useful variables to the environment which can be uses in rules and fallback
    files.

    :param config_file: the template
    :param server: if None this defaults to 0.0.0.0/0
    :param protocol: if None this defaults to 'udp'
    :returns: the rendered template as string
    """
    config_data_file = resources.get_config_file()
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(config_data_file)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    with open(config_data_file, "r") as config_data:
        config_data_dict = yaml.safe_load(config_data)
        if server:
            config_data_dict["vpn_remote"] = server["ip_address"]
        else:
            config_data_dict["vpn_remote"] = "0.0.0.0/0"

        if protocol:
            config_data_dict["vpn_protocol"] = protocol
        else:
            config_data_dict["vpn_protocol"] = "udp"
            protocol = "udp"

        if protocol == "udp":
            config_data_dict["vpn_port"] = "1194"
        elif protocol == "tcp":
            config_data_dict["vpn_port"] = "443"
        else:
            raise TypeError("Unknown protocol '{}'.".format(protocol))

        default_ip, default_iface = get_default_gateway(ipv6=False)
        if default_iface:
            try:
                interface_addresses = get_interface_addresses(default_iface)
                config_data_dict["gateway"] = {
                    "ip_address": default_ip,
                    "interface": default_iface,
                }
                config_data_dict["lan"] = interface_addresses
            except KeyError:
                config_data_dict["gateway"] = {}
                config_data_dict["lan"] = {}

        config_data_dict = merge_environment(config_data_dict)
        template = env.get_template(os.path.basename(config_file))
        return template.render(config_data_dict)


@user.needs_root
def read_config(config_file, server=None, protocol=None):
    """High-level abstraction for the render_template method

    :param config_file: the template
    :param server: the server as dict or None
    :param protocol: the used protocol as string. may be one of 'udp' or 'tcp'
    :returns: the rendered template file as dictionary
    """

    rendered_template = render_template(config_file, server, protocol)
    return yaml.safe_load(rendered_template)


class IptablesPrettyFormatter(Formatter):
    """Pretty format for iptables"""

    def format_table_header(self, table, sep="+"):
        """Format the table header

        :param object table: An iptables table
        :param sep: Fill with separator
        :returns: the table surrounded by line filled with sep
        """

        if is_table_v6(table):
            version = "v6"
        else:
            version = "v4"

        prefix = sep * 2
        string = table.name.upper()
        suffix = sep * (self.max_line_length - 5 - len(version) - len(string))

        table_header = "{} {} {} {}".format(prefix, string, version, suffix)
        return table_header

    def format_chain_header(self, chain, sep="="):
        """Format the chain header

        :param object chain: An iptables chain
        :param sep: Fill or separator
        :returns: the chain centered in a filled line with sep
        """
        policy = chain.get_policy()
        if policy:
            policy_s = policy.name
        else:
            policy_s = "None"

        if chain.is_builtin():
            packet_counter, byte_counter = chain.get_counters()
            packet_counter_s = self._format_counter(packet_counter, true_byte=False)
            byte_counter_s = self._format_counter(byte_counter)

            counter_output = "packets: {:>4} bytes: {:>4}".format(
                packet_counter_s, byte_counter_s
            )

            string = "{} ({:^6}) [{}]".format(chain.name, policy_s, counter_output)
        else:
            string = "{} ({:^6})".format(chain.name, policy_s)

        return self.center_string(string, sep)

    @staticmethod
    def _format_iprange(iprange):
        """Format an iprange to cidr notation

        :param iprange: An iprange as string
        :returns: iprange in cidr notation
        """

        if iprange.startswith("!"):
            return "!" + str(netaddr.IPNetwork(iprange.lstrip("!")).cidr)

        return str(netaddr.IPNetwork(iprange).cidr)

    @staticmethod
    def _format_counter(counter, true_byte=True):
        if true_byte:
            multi = 1024
        else:
            multi = 1000

        kilo = multi
        mega = multi * kilo
        giga = multi * mega

        counter_s = ""
        if counter > giga:
            counter_s = str(int(counter / giga)) + "G"
        elif counter > mega:
            counter_s = str(int(counter / mega)) + "M"
        elif counter > kilo:
            counter_s = str(int(counter / kilo)) + "K"
        else:
            counter_s = str(counter)

        return counter_s

    def format_rule(self, rule, rule_number, sep="-"):
        """Format a rule

        :param object rule: An iptables rule
        :param rule_number: the number of the rule in the chain
        :param sep: Separator/Fill
        :returns: the formatted rule in 2 lines with a separating rule appended
        """

        # convert to short cidr notation
        src_net = IptablesPrettyFormatter._format_iprange(str(rule.src))
        dst_net = IptablesPrettyFormatter._format_iprange(str(rule.dst))

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

        packet_counter, byte_counter = rule.get_counters()
        packet_counter = self._format_counter(packet_counter, true_byte=False)
        byte_counter = self._format_counter(byte_counter)

        counter_output = "packets: {:>4} bytes: {:>4}".format(
            packet_counter, byte_counter
        )
        output += "{} [{}] {}".format(
            sep * (self.max_line_length - 6 - len(counter_output)),
            counter_output,
            sep * 2,
        )
        return output


def print_table(table, stream):
    formatter = IptablesPrettyFormatter()
    stream_file = formatter.get_stream_file(stream)

    table.refresh()
    table_header = formatter.format_table_header(table)
    print(table_header, file=stream_file)
    for chain in table.chains:
        chain_header = formatter.format_chain_header(chain)
        print(chain_header, file=stream_file)
        counter = 1
        for rule in chain.rules:
            rule_s = formatter.format_rule(rule, counter)
            print(rule_s, file=stream_file)
            counter += 1

    return formatter.get_output()


@user.needs_root
def to_string(tables=None, version="4", stream=False):
    """Formats tables, chains and rules. If stream is True print directly to
    stdout else collect all lines in formatter.output

    :param tables: list of valid netfilter tables defaults to all netfilter tables
    :param version: either '6' for ip6tables, '4' for iptables or 'all' for both
    :param stream: If true stream to stdout instead of formatter.output
    """

    output = ""
    if version in ("4", "all"):
        if tables is None:
            tables = Table.ALL

        for table_s in tables:
            table = Table(table_s)
            output += print_table(table, stream)

    if version in ("6", "all"):
        if tables is None:
            tables = Table6.ALL

        for table_s in tables:
            table = Table6(table_s)
            output += print_table(table, stream)

    return output


def print_iptables(tables=None, version="4"):
    """Convenience function to print given tables in version to stdout"""
    to_string(tables, version, stream=True)
