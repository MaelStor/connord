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

"""Module to check root access and acquire it if needed"""

import os
import functools
import subprocess
from connord import ConnordError


class UserError(ConnordError):
    """Thrown within this module"""


def is_root():
    """
    Returns true if user is root

    :return: True if effective uid is 0
    """
    return os.geteuid() == 0


def needs_root(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if is_root():
            return func(*args, **kwargs)
        else:
            raise PermissionError(
                "Function '{}' needs root access.".format(func.__name__)
            )

    return wrapper


def prompt_sudo():
    """
    Prompt for sudo password and change effective uid to root on success.

    :return: True if user has root access now
    """

    if os.geteuid() != 0:
        message = "[connord][sudo] password needed: "
        return subprocess.check_call("sudo -v -p '{}'".format(message), shell=True)

    return True


# TODO: check_root throws PermissionError
