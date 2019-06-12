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


import subprocess
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import time
import os
import re
import signal
from connord import ConnordError
from connord import iptables
from connord import servers
from connord import load
from connord import countries
from connord import areas
from connord import types
from connord import features
from connord import user
from connord import resources
from connord import update


class ConnectError(ConnordError):
    """Thrown within this module"""


def ping(server):
    """
    Ping a server
    :param dict server: A server as dictionary
    :returns: copy of server with additional key 'ping'
    """

    server_copy = server.copy()
    pattern = re.compile(r"rtt .* = ([\d\.]+)/([\d\.]+)/([\d\.]+)/.* ms")
    ip_address = server["ip_address"]
    with subprocess.Popen(
        ["ping", "-q", "-n", "-c", "1", "-l", "1", "-W", "1", ip_address],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as ping_:

        out, _ = ping_.communicate()
        mat = pattern.search(out.decode())
        if mat:
            server_copy["ping"] = float(mat.group(2))
        else:
            server_copy["ping"] = None

        return server_copy


def ping_servers_parallel(servers_):
    """
    Ping a list of servers
    :param list servers_: List of servers
    :returns: List of servers with ping time
    """
    worker_count = cpu_count() + 1
    with ThreadPool(processes=worker_count) as pool:
        results = []
        for server in servers_:
            results.append(pool.apply_async(ping, (server,)))

        pinged_servers = []
        for result in results:
            pinged_servers.append(result.get())

        return pinged_servers


def filter_servers(
    servers_, netflix, countries_, areas_, features_, types_, load_, match
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

    return servers_


def filter_best_servers(servers_):
    servers_ = servers_.copy()
    servers_ = sorted(servers_, key=lambda k: k["load"])
    if len(servers_) > 10:
        servers_ = servers_[:10]
    servers_ = ping_servers_parallel(servers_)
    servers_ = sorted(servers_, key=lambda k: k["ping"])
    return servers_


@user.needs_root
def connect_to_specific_server(domain, openvpn, daemon, protocol):
    server = servers.get_server_by_domain(domain)
    if server:
        return run(server, openvpn, daemon, protocol)

    raise ConnectError("Could not find server with domain {}.".format(domain))


@user.needs_root
def connect(
    domain,
    countries_,
    areas_,
    features_,
    types_,
    netflix,
    load_,
    match,
    daemon,
    config_,
    openvpn,
    protocol,
):

    iptables.reset()

    if domain != "best":
        return connect_to_specific_server(domain, openvpn, daemon, protocol)

    if protocol:
        feature = "openvpn" + protocol
        if features_ is None:
            features_ = [feature]
        elif feature in features_:
            pass
        else:
            features_.append("openvpn" + protocol)

    servers_ = servers.get_servers()
    servers_ = filter_servers(
        servers_, netflix, countries_, areas_, features_, types_, load_, match
    )

    best_servers = filter_best_servers(servers_)
    for server in best_servers:
        if server["ping"] is not None:
            return run(server, openvpn, daemon, protocol)

    raise ConnectError("No server found to establish a connection.")


def add_openvpn_cmd_option(openvpn_cmd, flag, option=None):
    if flag not in openvpn_cmd:
        openvpn_cmd.append(flag)
        if option:
            openvpn_cmd.append(option)
    return openvpn_cmd


@user.needs_root
def run_openvpn(domain, openvpn, daemon, protocol):
    chroot_dir = "/var/openvpn"
    os.makedirs(chroot_dir, mode=0o700, exist_ok=True)

    openvpn_options = []
    if openvpn:
        openvpn_options = openvpn.split()

    cmd = ["openvpn"]
    for option in openvpn_options:
        cmd.append(option)

    if daemon:
        cmd = add_openvpn_cmd_option(cmd, "--daemon")

    try:
        config_file = resources.get_ovpn_config(domain, protocol)
    except resources.ResourceNotFoundError:
        update.update(force=True)  # give updating a try else let the error pass through
        config_file = resources.get_ovpn_config(domain, protocol)

    cmd = add_openvpn_cmd_option(cmd, "--config", option=config_file)

    credentials_file = resources.get_credentials_file(create=True)
    cmd = add_openvpn_cmd_option(cmd, "--auth-user-pass", option=credentials_file)
    cmd = add_openvpn_cmd_option(cmd, "--auth-nocache")
    cmd = add_openvpn_cmd_option(cmd, "--auth-retry", option="nointeract")

    cmd = add_openvpn_cmd_option(cmd, "--script-security", option="2")
    cmd = add_openvpn_cmd_option(
        cmd, "--up", option="/etc/openvpn/client/openvpn_up_down.bash"
    )

    cmd = add_openvpn_cmd_option(
        cmd, "--down", option="/etc/openvpn/client/openvpn_up_down.bash"
    )
    cmd = add_openvpn_cmd_option(cmd, "--down-pre")
    cmd = add_openvpn_cmd_option(cmd, "--redirect-gateway")

    try:
        with subprocess.Popen(cmd) as ovpn:
            _, _ = ovpn.communicate()
    except KeyboardInterrupt:
        time.sleep(1)

    if not daemon:
        iptables.reset(fallback=True)

    return True


@user.needs_root
def run(server, openvpn, daemon, protocol):
    iptables.apply_config_dir(server, protocol)

    domain = server["domain"]
    return run_openvpn(domain, openvpn, daemon, protocol)


@user.needs_root
def kill_openvpn():
    cmd = ["ps"]
    cmd.append("-A")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        out, _ = proc.communicate()
        for line in out.decode().splitlines():
            if "openvpn" in line:
                pid = int(line.split(None, 1)[0])
                os.kill(pid, signal.SIGTERM)
