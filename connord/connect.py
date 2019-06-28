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
"""An openvpn wrapper to connect to NordVPN servers"""


import subprocess
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from math import inf
import time
import os
import re
import signal
from connord import ConnordError, Printer
from connord import iptables
from connord import servers
from connord import load
from connord import countries
from connord import areas
from connord import types
from connord import features
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
            server_copy["ping"] = float("inf")

        printer = Printer()
        printer.info(
            "{:6}: ping: {}".format(server_copy["domain"], server_copy["ping"])
        )
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


# pylint: disable=too-many-arguments
def filter_servers(
    servers_, netflix, countries_, areas_, features_, types_, load_, match
):
    """Filter servers by keys from command-line options
    :param servers_: a list of servers given as dictionary
    :param netflix: Boolean if servers should be filtered to netflix optimized servers
    :param countries_: a list of countries each given as string
    :param areas_: a list of areas each given as string
    :param features_: a list of features each given as string
    :param types_: a list of types each given as string
    :param load_: depending on match filter max, min or equal load servers
    :param match: may be 'max', 'min' or 'equal'
    :returns: the filtered list of servers
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
        if "obfuscated" in types_:
            raise ConnectError("Connecting to obfuscated servers isn't supported yet.")

        servers_ = types.filter_servers(servers_, types_)
    if features_:
        servers_ = features.filter_servers(servers_, features_)

    # Filter out obfuscated servers. Not supported yet
    filtered_servers = [
        server
        for server in servers_
        if not types.has_type(server, "Obfuscated Servers")
    ]

    return filtered_servers


def filter_best_servers(servers_):
    """Filter servers by lowest load and ping

    :param servers_: list of servers each given as dictionary
    :returns: the filtered list of servers
    """
    servers_ = servers_.copy()
    servers_ = sorted(servers_, key=lambda k: k["load"])
    if len(servers_) > 10:
        servers_ = servers_[:10]
    servers_ = ping_servers_parallel(servers_)
    servers_ = sorted(servers_, key=lambda k: k["ping"])
    return servers_


def connect_to_specific_server(domain, openvpn, daemon, protocol):
    """Connect to a specific server

    :param domain: list of domains which holds one value like gb111
    :param openvpn: string of options to pass-through to openvpn
    :param daemon: True if the openvpn shall be run in daemon mode
    :param protocol: may be one of 'udp' or 'tcp'
    :returns: True if openvpn was run successfully
    """
    server = servers.get_server_by_domain(domain[0])
    if types.has_type(server, "Obfuscated Servers"):
        raise ConnectError("Connecting to obfuscated servers isn't supported yet.")
    return run_openvpn(server, openvpn, daemon, protocol)


# pylint: disable=too-many-locals
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
    openvpn,
    protocol,
):
    """High-level function to connect to a openvpn server. Filters servers and
    tries to connect to an openvpn server 'max_retries' times or else raise an
    exception.

    :param domain: list of domains. defaults to one value 'best'.
    :param countries_: list of countries
    :param areas_: list of areas
    :param features_: list of features
    :param types_: list of types
    :param netflix: True to filter netflix optimized servers
    :param load_: depending on match, filter by max, min or equal load servers
    :param match: may be 'max', 'min' or 'equal'
    :param daemon: True if openvpn shall run in daemon mode
    :param config_: the path to the openvpn configuration file
    :param openvpn: options to pass-through to openvpn as string
    :param protocol: may be 'udp' or 'tcp'
    :returns: True if running openvpn was successful
    :raises: ConnectError
    """

    if "best" not in domain:
        return connect_to_specific_server(domain, openvpn, daemon, protocol)

    servers_ = servers.get_servers()
    servers_ = filter_servers(
        servers_, netflix, countries_, areas_, features_, types_, load_, match
    )

    best_servers = filter_best_servers(servers_)
    max_retries = 3
    printer = Printer()
    for i, server in enumerate(best_servers):
        if i == max_retries:
            raise ConnectError("Maximum retries reached.")

        if server["ping"] != inf:
            printer.info("Trying to connect to {}".format(server["domain"]))
            if run_openvpn(server, openvpn, daemon, protocol):
                return True
            # else give the next server a try
        else:
            raise ConnectError("No server left with a valid ping.")

    raise ConnectError("No server found to establish a connection.")


# TODO: Rename to OpenvpnCommandPanicError
class OpenvpnCommandPanic(ConnectError):
    """Raised when something went wrong running openvpn"""

    def __init__(self, problem, message=None):
        """Initialize

        :param problem: string to describe what went wrong
        :param message: If not None apply default message.
        """
        if not message:
            message = "Running openvpn failed: {}".format(problem)

        super().__init__(message)
        self.problem = problem


class OpenvpnCommand:
    """Wraps openvpn"""

    def __init__(self, server, openvpn, daemon, protocol):
        """ Init

        :param server: a server dictionary
        :param openvpn: openvpn options as one string
        :param daemon: True if openvpn shall be run in daemon mode
        :param protocol: 'udp' or 'tcp'
        """
        self.server = server
        self.domain = server["domain"]
        self.openvpn_options = openvpn
        self.daemon = daemon
        self.protocol = protocol
        self.cmd = ["openvpn"]

    def _add_openvpn_cmd_option(self, flag, *args):
        """Convenience function to add an option to the command list

        :param flag: the --flag
        :param args: possible arguments for flag
        """
        if flag.startswith("-"):
            if flag not in self.cmd:
                self.cmd.append(flag)
                for arg in args:
                    self.cmd.append(arg)
        else:  # flag seems to be an argument and can be added without checks
            self.cmd.append(flag)

    @staticmethod
    def _format_flag(flag):
        """Return a formatted flag

        :param flag: an option without the necessary leading '--'
        """
        return "--{}".format(flag)

    def _forge_number(self, key, value):
        """Converts a number value to string and adds the option to self.cmd

        :param key: the flag
        :param value: the number value
        """
        flag = self._format_flag(key)
        self._add_openvpn_cmd_option(flag, str(value))

    def _forge_string(self, key, value):
        """Handles string values and adds the option to self.cmd. The key
        auth-user-pass needs special treatment since the value can be 'built-in'
        to use the predefined path to the credentials file.

        :param key: the flag
        :param value: the value related to the flag
        """
        flag = self._format_flag(key)
        if key == "auth-user-pass":
            if value == "built-in":
                creds_file = resources.get_credentials_file()
            else:
                creds_file = value

            self._add_openvpn_cmd_option(flag, creds_file)
        else:
            self._add_openvpn_cmd_option(flag, value)

    def _forge_bool(self, key, value):
        """Handles boolean values to be added to the final command.

        :param key: the flag
        :param value: the value related to the flag
        """
        if value in (True, "True", "true"):
            flag = self._format_flag(key)
            self._add_openvpn_cmd_option(flag)

    def _forge_list(self, key, list_):
        """Handles list values to be added to the final command. The 'scripts' key
        needs special treatment for the 'built-in' value.

        :param key: the flag
        :param list_: the list of strings
        """
        if key == "scripts":
            self._forge_scripts(list_)
        else:
            flag = self._format_flag(key)
            if list_:
                self._add_openvpn_cmd_option(flag)
                for value in list_:
                    self._add_openvpn_cmd_option(value)
            else:
                self._add_openvpn_cmd_option(flag)

    @staticmethod
    def _format_script_arg(script_name, path, file_):
        """Format the argument for the scripts key to combine the script path and the
        path to the environment file in one string. Handles the special value 'built-in'
        to resolve to the built-in path of the corresponding script.
        :param script_name: name of the script
        :param path: either 'built-in' or a user-defined path
        :param file_: The name for the file created by the script
        :returns: the formatted argument.
        """
        if path == "built-in":
            script_path = resources.get_scripts_file(script_name=script_name)
            env_dir = resources.get_stats_dir()
            env_file = "{}/{}".format(env_dir, file_)
        else:
            script_path = path
            env_file = file_

        return "'{}' {}".format(script_path, env_file)

    def _forge_scripts(self, scripts):
        """Adds the formatted script paths to the resulting command-line

        :param scripts: list of scripts served as dictionaries
        """
        for script in scripts:
            name = script["name"]
            flag = self._format_flag(name)
            path = script["path"]
            file_ = script["creates"]
            if name in ("up", "down"):
                arg = self._format_script_arg("openvpn_up_down.bash", path, file_)
            elif name == "ipchange":
                arg = self._format_script_arg("openvpn_ipchange.bash", path, file_)
            else:
                if path == "built-in":
                    raise resources.ResourceNotFoundError(
                        path, "No built-in found for {!r}.".format(name)
                    )

                arg = self._format_script_arg(name, path, file_)

            self._add_openvpn_cmd_option(flag, arg)

    def _forge_command_line(self):
        """Add the command-line arguments relevant for the openvpn command"""
        if self.openvpn_options:
            for option in self.openvpn_options.split():
                self._add_openvpn_cmd_option(option)

        if self.daemon:
            self._add_openvpn_cmd_option("--daemon")

    def _forge_config(self):
        """Add the openvpn options from 'config.yml' to the openvpn command"""
        openvpn_config = resources.get_config()["openvpn"]
        for k, v in openvpn_config.items():
            if isinstance(v, bool) or v in ("true", "True", "false", "False"):
                self._forge_bool(k, v)
            elif isinstance(v, list):
                self._forge_list(k, v)
            elif isinstance(v, (int, float)):
                self._forge_number(k, v)
            else:
                self._forge_string(k, v)

    def has_flag(self, flag):
        """Return true if the flag is present in the current openvpn command"""
        if flag.startswith("--"):
            return flag in self.cmd

        return "--{}".format(flag) in self.cmd

    def forge_ovpn_config(self, config_file=None):
        """Remove all openvpn command-line arguments from the ovpn config file
        to prevent overriding the command-line. Use final temporary file as
        value for the --config flag

        :param config_file: path to an optional configuration file
        """
        if not config_file:
            config_file = resources.get_ovpn_config(self.domain, self.protocol)

        config_tmp = resources.get_ovpn_tmp_path()

        with open(config_file, "r") as config_fd:
            lines = config_fd.readlines()
        with open(config_tmp, "w") as config_fd:
            for line in lines:
                if line != "\n":
                    # TODO: improve to flag = line.split(None, 1)[0]
                    fake_line = line.rstrip() + " $"
                    flag, _ = fake_line.split(maxsplit=1)
                    if not self.has_flag(flag):
                        config_fd.write(line)
                else:
                    config_fd.write(line)

        os.chmod(config_tmp, mode=0o640)
        self._add_openvpn_cmd_option("--config", config_tmp)

    def forge(self):
        """The high-level command to assemble the openvpn cmd. Adds the --config
        and the --writepid flag flag if not present yet."""
        self._forge_command_line()
        self._forge_config()
        if "--config" not in self.cmd:
            try:
                self.forge_ovpn_config()
            except resources.ResourceNotFoundError:
                update.update(
                    force=True
                )  # give updating a try else let the error happen
                self.forge_ovpn_config()
        else:
            index = self.cmd.index("--config")
            config_file = self.cmd[index + 1]
            self.cmd.remove("--config")
            self.cmd.remove(config_file)
            self.forge_ovpn_config(config_file=config_file)

        if not self.has_flag("--writepid"):
            pid_dir = resources.get_stats_dir(create=True)
            pid_file = pid_dir + "/openvpn.pid"
            self._add_openvpn_cmd_option("--writepid", pid_file)

    def is_daemon(self):
        """Return true if --daemon flag is in the current openvpn command"""
        return "--daemon" in self.cmd

    @staticmethod
    def cleanup():
        """Cleanup temporary stuff and reset iptables."""
        resources.remove_stats_dir()
        iptables.reset(fallback=True)

    @staticmethod
    def is_running(process):
        """Return true if openvpn is running"""
        return not bool(process.poll())

    def panic(self, process, problem):
        """High-level command to shutdown openvpn and cleanup temporary files.

        :raises OpenvpnCommandPanic
        """
        if self.is_running(process):
            process.kill()

        self.cleanup()
        resources.remove_ovpn_tmp_file()
        raise OpenvpnCommandPanic(problem)

    def run(self):
        """High-level command to run openvpn with the assembled command-line.
        Shuts down openvpn after a timeout. Waits this time for openvpn to startup
        and writes the environment files from the scripts. As soon as they are
        present iptables rules are applied. If something goes wrong call the panic
        method

        :returns: True if everything went fine or running in daemon mode.
        """

        config_dict = resources.get_config()["openvpn"]
        self.cleanup()

        printer = Printer()
        printer.info("Running openvpn with '{}'".format(self.cmd))
        with subprocess.Popen(self.cmd) as ovpn:
            # give openvpn a maximum of 60 seconds to startup. A lower value is bad if
            # asked for username/password.
            # pylint: disable=unused-variable
            for i in range(300):
                try:
                    if self.is_running(ovpn):
                        # delay initialization of iptables until resource files are
                        # created. If none are created the delay still applies as normal
                        # timeout
                        time.sleep(0.2)
                        for script in config_dict["scripts"]:
                            stage = script["stage"]
                            if stage in ("up", "always"):
                                resources.get_stats_file(
                                    stats_name=script["creates"], create=False
                                )

                    else:
                        self.panic(ovpn, "Openvpn process stopped unexpected.")

                    if iptables.apply_config_dir(self.server, self.protocol):
                        resources.write_stats(self.server, stats_name="server")

                        stats_dict = resources.get_stats()
                        stats_dict["last_server"] = {}
                        stats_dict["last_server"]["domain"] = self.domain
                        stats_dict["last_server"]["protocol"] = self.protocol
                        resources.write_stats(stats_dict)
                    else:
                        self.panic(ovpn, "Applying iptables failed.")

                    break
                except resources.ResourceNotFoundError:
                    pass
            ### for
            else:
                self.panic(ovpn, "Timeout reached.")

            if self.is_running(ovpn):
                ovpn.wait()

        return True


def run_openvpn(server, openvpn, daemon, protocol):
    """Intermediate function to setup openvpn and wrap the final run."""
    openvpn_cmd = OpenvpnCommand(server, openvpn, daemon, protocol)
    openvpn_cmd.forge()

    retval = False
    try:
        retval = openvpn_cmd.run()
    except KeyboardInterrupt:
        retval = True
        time.sleep(1)

    if not openvpn_cmd.is_daemon():
        resources.remove_ovpn_tmp_file()
        openvpn_cmd.cleanup()

    return retval


def kill_openvpn(pid=None):
    """Kill all openvpn processes currently running or if pid is given this process.
    :param pid: integer with an process id. Can be any pid but intention is to shutdown
    openvpn this way. If None all openvpn process are shutdown targets
    """
    if pid:
        os.kill(pid, signal.SIGTERM)
    else:
        cmd = ["ps"]
        cmd.append("-A")
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
            out, _ = proc.communicate()
            for line in out.decode().splitlines():
                if "openvpn" in line:
                    pid = int(line.split(None, 1)[0])
                    os.kill(pid, signal.SIGTERM)
