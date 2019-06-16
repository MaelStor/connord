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
import getpass
import tempfile
from shutil import rmtree
import yaml
from pkg_resources import resource_filename
from connord import ConnordError
from connord import user

__NORDVPN_DIR = "/etc/openvpn/client/nordvpn"
__SCRIPTS_DIR = "/etc/openvpn/client/scripts"
__CONFIG_DIR = "/etc/connord"
__CONFIG_FILE = __CONFIG_DIR + "/config.yml"
__RUN_DIR = "/var/run/connord"

__DATABASE_FILE = resource_filename(__name__, "db/connord.sqlite3")


class ResourceNotFoundError(ConnordError):
    """Raised when a resource is requested but doesn't exist"""

    def __init__(self, resource_file, message=None):

        # if a message is given use it else use the one defined here
        if message:
            super().__init__(message)
        else:
            super().__init__("Resource does not exist: {!r}".format(resource_file))

        #: A string representing a file path
        self.resource_file = resource_file


class MalformedResourceError(ConnordError):
    def __init__(self, resource_file, problem, problem_mark):
        super().__init__(
            "Malformed resource: {!r}\n{!s}\n{!s}".format(
                resource_file, problem, problem_mark
            )
        )

        self.resource_file = resource_file
        self.problem = problem
        self.problem_mark = problem_mark


def list_dir(directory, filetype=None):
    files = os.listdir(directory)

    if filetype:
        files = [_file for _file in files if _file.endswith("." + filetype)]

    full_path_files = [directory + "/" + _file for _file in files]

    return full_path_files


def get_zip_dir(create=True):
    """Returns the directory where nordvpn related zip files are stored

    :param create: if True create the directory
    :returns: the zip directory
    :rtype: string
    :raises: ``ResourceNotFoundError`` when `zip_dir` does not exist
    """

    zip_dir = __NORDVPN_DIR
    if not os.path.exists(zip_dir):
        if create:
            os.makedirs(zip_dir)
        else:
            raise ResourceNotFoundError(zip_dir)

    return zip_dir


def get_zip_path(zip_name=None):
    """Return the absolute path to `zip_name` with the output of the
    ``get_zip_dir()`` as base directory. Does not check if the path
    exists.

    :param zip_name: name of the zip file
    :ptype: string
    :default: None
    :returns: the path to the zip file
    :rtype: string
    """

    if not zip_name:
        zip_name = "ovpn.zip"

    zip_dir = get_zip_dir(create=False)
    return zip_dir + "/" + zip_name


def get_zip_file(zip_name=None, create_dirs=True):
    """Return the absolute path to `zip_name` with the output of the
    ``get_zip_dir()`` as base directory. Verifies if the file exists.

    :param zip_name: name of the zip file
    :ptype: string
    :default: None
    :returns: the path to the zip file
    :rtype: string
    :raises: ResourceNotFoundError if the `zip_path` does not exist
    """

    if not zip_name:
        zip_name = "ovpn.zip"

    zip_dir = get_zip_dir(create=create_dirs)
    zip_path = zip_dir + "/" + zip_name
    if os.path.exists(zip_path):
        return zip_path

    raise ResourceNotFoundError(zip_path)


def get_database_file(create=True):
    """Return the database file path

    :param create: if True create the database file (not the directory)
    :returns: the file path as string
    """

    database_file = __DATABASE_FILE
    if not os.path.exists(database_file):
        if create:
            with open(database_file, "w"):
                pass
        else:
            raise ResourceNotFoundError(database_file)

    return database_file


def file_has_permissions(path, permissions=0o600):
    """Check file permissions"""

    stats = os.stat(path)
    return stats.st_mode & 0o777 == permissions


def verify_file_permissions(path, permissions=0o600):
    """Verify file permissions"""

    if not file_has_permissions(path, permissions):
        raise PermissionError(
            "Unsafe file permissions: {!r} should have mode: {!r}.".format(
                path, oct(permissions)
            )
        )
    return True


def get_credentials_dir(create=True):
    creds_dir = __NORDVPN_DIR
    if not os.path.exists(__NORDVPN_DIR):
        if create:
            os.makedirs(__NORDVPN_DIR, mode=0o755)
        else:
            raise ResourceNotFoundError(__NORDVPN_DIR)

    return creds_dir


@user.needs_root
def get_credentials_file(file_name="credentials", create=True):
    creds_dir = get_credentials_dir()
    creds_file = "{}/{}".format(creds_dir, file_name)
    if not os.path.exists(creds_file):
        if create:
            create_credentials_file(creds_file)
        else:
            raise ResourceNotFoundError(creds_file)

    verify_file_permissions(creds_file)
    return creds_file


def _get_username():
    return input("Enter username: ")


def create_credentials_file(credentials_file):
    username = _get_username()
    password = getpass.getpass("Enter password: ")

    with open(credentials_file, "w") as creds_fd:
        creds_fd.write(username + "\n")
        creds_fd.write(password + "\n")

    password = None
    os.chmod(credentials_file, mode=0o600)
    return credentials_file


@user.needs_root
def get_ovpn_dir(create=True):
    if os.path.exists(__NORDVPN_DIR):
        return __NORDVPN_DIR

    raise ResourceNotFoundError(__NORDVPN_DIR)


@user.needs_root
def get_ovpn_protocol_dir(protocol="udp"):
    base_dir = get_ovpn_dir()
    config_dir = "{}/ovpn_{}".format(base_dir, protocol)

    if os.path.exists(config_dir):
        return config_dir

    raise ResourceNotFoundError(config_dir)


@user.needs_root
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
    config_dir = get_config_dir()
    return list_dir(config_dir, filetype)


def get_config_file(config_name="config.yml"):
    config_dir = get_config_dir()
    config_file = "{}/{}".format(config_dir, config_name)
    if os.path.exists(config_file):
        return config_file

    raise ResourceNotFoundError(config_file)


def get_config():
    config_file = get_config_file()
    try:
        with open(config_file, "r") as config_fd:
            return yaml.safe_load(config_fd)
    except yaml.parser.ParserError as error:
        raise MalformedResourceError(
            config_file, error.problem, str(error.problem_mark)
        )


def write_config(config_dict):
    config_file = get_config_file()
    if not isinstance(config_dict, dict):
        raise TypeError(
            # pylint: disable=line-too-long
            "Could not write to {!r}: Invalid type: Found {!s} but expected {!s}.".format(
                config_file, type(config_dict), dict
            )
        )

    with open(config_file, "w") as config_fd:
        yaml.dump(config_dict, config_fd, default_flow_style=False)


@user.needs_root
def get_stats_dir(create=True):
    stats_dir = __RUN_DIR
    if not os.path.exists(stats_dir):
        if create:
            os.makedirs(stats_dir, mode=0o750)
        else:
            raise ResourceNotFoundError(stats_dir)

    return stats_dir


@user.needs_root
def remove_stats_dir():
    try:
        stats_dir = get_stats_dir(create=False)
        rmtree(stats_dir)
    except ResourceNotFoundError:
        pass

    return True


def list_stats_dir(filetype=None):
    stats_dir = get_stats_dir()
    return list_dir(stats_dir, filetype)


@user.needs_root
def get_stats_file(stats_name=None, create=True):
    """Get stats file"""
    if not stats_name:
        stats_name = "stats"

    stats_dir = get_stats_dir(create)
    stats_file = "{}/{}".format(stats_dir, stats_name)
    if not os.path.exists(stats_file):
        if create:
            with open(stats_file, "w"):
                pass
        else:
            raise ResourceNotFoundError(stats_file)

    return stats_file


@user.needs_root
def get_stats(stats_name="stats"):
    stats_file = get_stats_file(stats_name=stats_name)
    try:
        with open(stats_file, "r") as stats_fd:
            stats_dict = yaml.safe_load(stats_fd)
            if not stats_dict:
                stats_dict = {}

            return stats_dict
    except yaml.parser.ParserError as error:
        raise MalformedResourceError(stats_file, error.problem, str(error.problem_mark))


@user.needs_root
def write_stats(stats_dict, stats_name="stats"):
    stats_file = get_stats_file(stats_name=stats_name)
    if not isinstance(stats_dict, dict):
        raise TypeError(
            # pylint: disable=line-too-long
            "Could not write to {!r}: Invalid type: Found {!s} but expected {!s}.".format(
                stats_file, type(stats_dict), dict
            )
        )

    with open(stats_file, "w") as stats_fd:
        yaml.dump(stats_dict, stats_fd, default_flow_style=False)


def read_pid(pid_name="openvpn.pid"):
    pid_file = get_stats_file(stats_name=pid_name)
    with open(pid_file, "r") as pid_fd:
        return int(pid_fd.readline())


def get_ovpn_tmp_path():
    temp_dir = tempfile.gettempdir()
    return "{}/{}".format(temp_dir, "ovpn.conf")


def remove_ovpn_tmp_file():
    temp_dir = tempfile.gettempdir()
    os.remove("{}/{}".format(temp_dir, "ovpn.conf"))
