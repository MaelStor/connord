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
from connord import ConnordError
from connord import user

CREDENTIAL_FILES = {
    "user": "~/.connord/credentials",
    "root": "/etc/openvpn/client/nordvpn/credentials",
}


class CredentialsError(ConnordError):
    """Thrown within this module"""


def verify_permissions(credential_file):
    """Verify file permissions to be readable and writable only by the
    user itself.

    Parameters
    ----------
    credential_file : str
        Path to the credential file

    Returns
    -------
    bool
        True if file permissions are octal 0600

    """
    stats = os.stat(credential_file)
    return oct(stats.st_mode & 0o777) == "0o600"


def get_credentials_file():
    for credential_file in CREDENTIAL_FILES.values():
        if os.path.exists(os.path.expanduser(credential_file)):
            if verify_permissions(credential_file):
                return credential_file
            else:
                raise CredentialsError(
                    "Unsafe permissions on '{}'.".format(credential_file)
                )
    else:
        return None


def create_credentials_file():
    credentials_file = get_credentials_file()
    if not credentials_file:
        credentials_file = str()
        credentials_dir = str()
        if user.is_root():
            credentials_file = CREDENTIAL_FILES["root"]
            credentials_dir = os.path.dirname(credentials_file)
        else:
            credentials_file = CREDENTIAL_FILES["user"]
            credentials_dir = os.path.dirname(os.path.expanduser(credentials_file))

        os.makedirs(credentials_dir, mode=0o755, exist_ok=True)
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")

        with open(credentials_file, "w") as creds_fd:
            creds_fd.write(username + "\n")
            creds_fd.write(password + "\n")

        password = None
        os.chmod(credentials_file, 0o600)

    return credentials_file
