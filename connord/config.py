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

# TODO: Rename config module to resources

import os
import yaml
from pkg_resources import resource_filename, resource_listdir
from connord import ConnordError
from connord import user

__NORDVPN_DIR = "/etc/openvpn/client/nordvpn"
__SCRIPTS_DIR = "/etc/openvpn/client/scripts"
__CONFIG_DIR = "/etc/connord"
__CONFIG_FILE = __CONFIG_DIR + "/config.yml"
__RUN_DIR = "/var/run/connord"


class ResourceNotFoundError(ConnordError):
    """Throw when a resource is not available"""

    def __init__(self, resource_file, message=None):
        if message:
            super().__init__(message)
        else:
            super().__init__("Resource does not exist: {!r}".format(resource_file))

        self.resource_file = resource_file


def file_has_permissions(path, permissions=0o600):
    """Check file permissions"""

    stats = os.stat(path)
    return stats.st_mode & 0o777 == permissions


def verify_file_permissions(path, permissions=0o600):
    """Verify file permissions"""

    if not file_has_permissions(path, permissions):
        raise PermissionError(
            "Unsafe file permissions: {!r} should have mode: {!r}.".format(
                path, permissions
            )
        )
    return True


@user.needs_root
def get_credentials_file(file_name="credentials"):
    creds_file = "{}/{}".format(__NORDVPN_DIR, file_name)
    if os.path.exists(creds_file):
        if verify_file_permissions(creds_file):
            return creds_file

    raise ResourceNotFoundError(creds_file)


def get_ovpn_dir():
    if os.path.exists(__NORDVPN_DIR):
        return __NORDVPN_DIR

    raise ResourceNotFoundError(__NORDVPN_DIR)


def get_ovpn_protocol_dir(protocol="udp"):
    config_dir = "{}/ovpn_{}".format(__NORDVPN_DIR, protocol)

    if os.path.exists(config_dir):
        return config_dir

    raise ResourceNotFoundError(config_dir)


def get_ovpn_config(domain, protocol="udp"):
    config_dir = get_ovpn_protocol_dir(protocol)
    if ".nordvpn.com" not in domain:
        domain = "{}.nordvpn.com".format(domain)

    config_file = "{}/{}.{}.ovpn".format(config_dir, domain, protocol)
    if os.path.exists(config_file):
        return config_file

    raise ResourceNotFoundError(config_file)


def get_scripts_dir():
    if os.path.exists(__SCRIPTS_DIR):
        scripts_dir = __SCRIPTS_DIR
    else:
        scripts_dir = resource_filename(__name__, "scripts")

    return scripts_dir


def get_scripts_file(script_name="openvpn_up_down.bash"):
    scripts_dir = get_scripts_dir()
    scripts_file = "{}/{}".format(scripts_dir, script_name)
    if os.path.exists(scripts_file):
        return scripts_file

    raise ResourceNotFoundError(scripts_file)


def get_config_dir():
    if os.path.exists(__CONFIG_DIR):
        config_dir = __CONFIG_DIR
    else:
        config_dir = resource_filename(__name__, "config")

    return config_dir


# TODO: has_config(filetype=None)


def list_config_dir(filetype=None):
    files = []
    if os.path.exists(__CONFIG_DIR):
        files = os.listdir(__CONFIG_DIR)
    else:
        files = resource_listdir(__name__, "config")

    if filetype:
        files = [_file for _file in files if _file.endswith("." + filetype)]

    config_dir = get_config_dir()
    full_path_files = [config_dir + "/" + _file for _file in files]

    return full_path_files


def get_config_file(config_name="config.yml"):
    config_dir = get_config_dir()
    config_file = "{}/{}".format(config_dir, config_name)
    if os.path.exists(config_file):
        return config_file

    raise ResourceNotFoundError(config_file)


def get_config():
    config_file = get_config_file()
    with open(config_file, "r") as config_fd:
        return yaml.safe_load(config_fd)


def write_config(config_dict):
    config_file = get_config_file()
    with open(config_file, "w") as config_fd:
        yaml.dump(config_dict, config_fd, default_flow_style=False)


@user.needs_root
def get_stats_dir(create=True):
    stats_dir = __RUN_DIR
    if create:
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir, mode=0o750)
    else:
        if not os.path.exists(stats_dir):
            raise ResourceNotFoundError(stats_dir)

    return stats_dir


@user.needs_root
def get_stats_file(stats_name="stats", create=True):
    stats_dir = get_stats_dir(create)
    stats_file = "{}/{}".format(stats_dir, stats_name)
    if create:
        if not os.path.exists(stats_file):
            with open(stats_file, "w"):
                pass
    else:
        if not os.path.exists(stats_file):
            raise ResourceNotFoundError(stats_file)

    return stats_file


@user.needs_root
def get_stats():
    stats_file = get_stats_file()
    with open(stats_file, "r") as stats_fd:
        stats_dict = yaml.safe_load(stats_fd)
        if not stats_dict:
            stats_dict = {}

        return stats_dict


@user.needs_root
def write_stats(stats_dict):
    stats_file = get_stats_file()
    with open(stats_file, "w") as stats_fd:
        yaml.dump(stats_dict, stats_fd, default_flow_style=False)
