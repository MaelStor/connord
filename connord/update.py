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

"""Update configuratio files of nordvpn
"""
# TODO: improve exception handling

import os
from shutil import move
from zipfile import ZipFile
from datetime import datetime, timedelta
import requests
from connord import ConnordError

__URL = "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip"
__DESTDIR = "/etc/openvpn/client/nordvpn"
__ZIP_PATH = __DESTDIR + "/ovpn.zip"
__ORIG_PATH = __DESTDIR + "/ovpn.orig.zip"
TIMEOUT = timedelta(days=1)


class UpdateError(ConnordError):
    """Raised during update"""


def init():
    """Initialize directories
    """
    try:
        os.makedirs(__DESTDIR, mode=0o750, exist_ok=True)
    except OSError as error:
        raise UpdateError("Error creating {}: '{!s}'".format(__DESTDIR, error))


def update_orig():
    """
    Move the original file to make room for the newly downloaded file
    """

    if os.path.exists(__ZIP_PATH):
        return move(__ZIP_PATH, __ORIG_PATH)

    return True


def get():
    """Get the zip file
    """
    if not update_orig():
        return False

    print("Downloading {} ...".format(__ZIP_PATH))
    with requests.get(__URL, stream=True) as response, open(__ZIP_PATH, "wb") as handle:
        for chunk in response.iter_content(chunk_size=512):
            handle.write(chunk)

    return True


def file_equals(_file, _other):
    """Compares the orig.zip file to the downloaded file
    : returns: False if file sizes differ
    """
    if os.path.exists(_file) and os.path.exists(_other):
        return os.path.getsize(_file) == os.path.getsize(_other)
    else:
        return False


def unzip():
    """Unzip the configuration files
    """
    print("Unzipping {} ...".format(__ZIP_PATH))
    with ZipFile(__ZIP_PATH) as zip_file:
        zip_file.extractall(__DESTDIR)


def update(force=False):
    """Update the nordvpn configuration files
    """
    init()
    if force:
        get()
        unzip()
    else:
        if update_needed():
            get()
            if not file_equals(__ORIG_PATH, __ZIP_PATH):
                unzip()
            else:
                print(__ZIP_PATH + " already up-to-date")
        else:
            next_update = datetime.fromtimestamp(os.path.getctime(__ZIP_PATH)) + TIMEOUT
            print("No update needed. Next update needed at {!s}".format(next_update))

    return True


def update_needed():
    """Check if an update is needed
    : returns: False if the zip file's creation time hasn't reached the timeout
               else True.
    """
    if os.path.exists(__ZIP_PATH):
        now = datetime.now()
        time_created = datetime.fromtimestamp(os.path.getctime(__ZIP_PATH))
        return now - TIMEOUT > time_created

    return True
