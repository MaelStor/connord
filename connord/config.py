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

import os
import yaml
from pkg_resources import resource_filename, resource_listdir
from connord import ConnordError
from connord import user

CONFIG_DIR = "/etc/connord"
CONFIG_FILE = CONFIG_DIR + "/config.yml"
RUN_DIR = "/var/run/connord"
STATS_FILE = RUN_DIR + "/stats"


class ConfigError(ConnordError):
    """Thrown within this module"""


def get_config_dir():
    config_dir = ""
    if os.path.exists(CONFIG_DIR):
        config_dir = CONFIG_DIR
    else:
        config_dir = resource_filename(__name__, "config")

    return config_dir

# TODO: has_config(filetype=None)


def list_config_dir(filetype=None):
    files = []
    if os.path.exists(CONFIG_DIR):
        files = os.listdir(CONFIG_DIR)
    else:
        files = resource_listdir(__name__, "config")

    if filetype:
        files = [_file for _file in files if _file.endswith("." + filetype)]

    config_dir = get_config_dir()
    full_path_files = [config_dir + "/" + _file for _file in files]

    return full_path_files


def get_config_file():
    config_file = ""
    if os.path.exists(CONFIG_FILE):
        config_file = CONFIG_FILE
    else:
        config_file = resource_filename(__name__, "config/config.yml")

    return config_file


def get_config():
    config_file = get_config_file()
    with open(config_file, "r") as config_fd:
        return yaml.safe_load(config_fd)


def write_config(config_dict):
    config_file = get_config_file()
    with open(config_file, "w") as config_fd:
        yaml.dump(config_dict, config_fd, default_flow_style=False)


@user.needs_root
def create_stats_file():
    if not os.path.exists(RUN_DIR):
        os.makedirs(RUN_DIR, mode=0o750)

    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w"):
            pass

    return STATS_FILE


@user.needs_root
def get_stats_file():
    return create_stats_file()


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
