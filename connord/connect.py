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
from connord import ConnordError
from connord import iptables
from connord import servers
from connord import load
from connord import countries
from connord import types
from connord import features
from connord import user
from connord import credentials


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
    ) as _ping:

        out, _ = _ping.communicate()
        mat = pattern.search(out.decode())
        if mat:
            server_copy["ping"] = float(mat.group(2))
        else:
            server_copy["ping"] = None

        return server_copy


def ping_servers_parallel(_servers):
    """
    Ping a list of servers
    :param list _servers: List of servers
    :returns: List of servers with ping time
    """
    worker_count = cpu_count() + 1
    with ThreadPool(processes=worker_count) as pool:
        results = []
        for server in _servers:
            results.append(pool.apply_async(ping, (server,)))

        pinged_servers = []
        for result in results:
            pinged_servers.append(result.get())

        return pinged_servers


def filter_servers(
    _servers, _netflix, _countries, _areas, _features, _types, _load, _match
):
    if _load:
        _servers = load.filter_servers(_servers, _load, _match)
    if _netflix:
        _servers = servers.filter_netflix_servers(_servers, _countries)
    if _countries:
        _servers = countries.filter_servers(_servers, _countries)
    if _areas:
        raise NotImplementedError("Area not implemented yet")
    if _types:
        _servers = types.filter_servers(_servers, _types)
    if _features:
        _servers = features.filter_servers(_servers, _features)

    return _servers


def filter_best_servers(_servers):
    _servers = sorted(_servers, key=lambda k: k["load"])
    if len(_servers) > 10:
        _servers = _servers[:10]
    _servers = ping_servers_parallel(_servers)
    _servers = sorted(_servers, key=lambda k: k["ping"])
    return _servers


@user.needs_root
def connect_to_specific_server(_domain, _openvpn, _daemon, _protocol):
    _server = servers.get_server_by_domain(_domain)
    if _server:
        return run(_server, _openvpn, _daemon, _protocol)
    else:
        raise ConnectError("Could not find server with domain {}.".format(_domain))


@user.needs_root
def connect(
    _domain,
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
):

    iptables.reset()

    if _domain != "best":
        return connect_to_specific_server(_domain, _openvpn, _daemon, _protocol)

    if _protocol:
        feature = "openvpn_" + _protocol
        if _features is None:
            _features = [feature]
        elif feature in _features:
            pass
        else:
            _features.append("openvpn_" + _protocol)

    _servers = servers.get_servers()
    _servers = filter_servers(
        _servers, _netflix, _countries, _areas, _features, _types, _load, _match
    )

    best_servers = filter_best_servers(_servers)
    for _server in best_servers:
        if _server["ping"] is not None:
            return run(_server, _openvpn, _daemon, _protocol)

    raise ConnectError("No server found to establish a connection.")


def add_openvpn_cmd_option(openvpn_cmd, flag, option=None):
    if flag not in openvpn_cmd:
        openvpn_cmd.append(flag)
        if option:
            openvpn_cmd.append(option)
    return openvpn_cmd


@user.needs_root
def run_openvpn(_domain, _openvpn, _daemon, _protocol):
    chroot_dir = "/var/openvpn"
    os.makedirs(chroot_dir, mode=0o700, exist_ok=True)

    openvpn_options = []
    if _openvpn:
        openvpn_options = _openvpn.split()

    cmd = ["openvpn"]
    for option in openvpn_options:
        cmd.append(option)

    if _daemon:
        cmd = add_openvpn_cmd_option(cmd, "--daemon")

    cmd = add_openvpn_cmd_option(cmd, "--chroot", option=chroot_dir)

    config_dir = "/etc/openvpn/client/nordvpn/ovpn_" + _protocol
    config_file = config_dir + "/" + _domain + "." + _protocol + ".ovpn"
    cmd = add_openvpn_cmd_option(cmd, "--config", option=config_file)

    credentials_file = credentials.get_credentials_file()
    if not credentials_file:
        credentials_file = credentials.create_credentials_file()
    cmd = add_openvpn_cmd_option(cmd, "--auth-user-pass", option=credentials_file)

    cmd = add_openvpn_cmd_option(cmd, "--script-security", option="2")
    cmd = add_openvpn_cmd_option(
        cmd, "--up", option="/etc/openvpn/client/openvpn_up_down.bash"
    )

    # executed in chroot directory so final path is
    # prefixed with /var/openvpn/...
    cmd = add_openvpn_cmd_option(
        cmd, "--down", option="/etc/openvpn/client/openvpn_up_down.bash"
    )
    cmd = add_openvpn_cmd_option(cmd, "--down-pre")
    cmd = add_openvpn_cmd_option(cmd, "--redirect-gateway")
    cmd = add_openvpn_cmd_option(cmd, "--auth-retry", option="nointeract")

    try:
        with subprocess.Popen(cmd) as ovpn:
            _, _ = ovpn.communicate()
    except KeyboardInterrupt:
        time.sleep(3)
        return True

    return True


@user.needs_root
def run(_server, _openvpn, _daemon, _protocol):
    iptables.apply_config_dir(_server, _protocol)

    domain = _server["domain"]
    return run_openvpn(domain, _openvpn, _daemon, _protocol)
