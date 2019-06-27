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

"""Update configuration files of nordvpn
"""
# TODO: improve exception handling

import os
from shutil import move, rmtree
from zipfile import ZipFile
from datetime import datetime, timedelta
import requests
from connord import ConnordError, Printer
from connord import resources
from connord import user
from connord import areas

__URL = "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip"
TIMEOUT = timedelta(days=1)


class UpdateError(ConnordError):
    """Raised during update"""


@user.needs_root
def update_orig():
    """
    Move the original file to make room for the newly downloaded file
    """

    try:
        zip_file = resources.get_zip_file(create_dirs=True)
    except resources.ResourceNotFoundError:
        return False

    move(zip_file, zip_file + ".orig")
    return True


def get():
    """Get the zip file
    """
    zip_path = resources.get_zip_path()
    update_orig()

    printer = Printer()
    spinner = printer.spinner("Downloading configuration files")
    with requests.get(__URL, stream=True, timeout=1) as response, open(
        zip_path, "wb"
    ) as zip_fd:
        chunk_size = 512
        for chunk in response.iter_content(chunk_size=chunk_size):
            spinner.next()
            zip_fd.write(chunk)

    spinner.finish()

    return True


def file_equals(file_, other_):
    """Compares the orig.zip file to the downloaded file
    : returns: False if file sizes differ
    """
    if os.path.exists(file_) and os.path.exists(other_):
        return os.path.getsize(file_) == os.path.getsize(other_)

    return False


def unzip():
    """Unzip the configuration files
    """

    printer = Printer()
    zip_dir = resources.get_zip_dir(create=True)
    zip_file = resources.get_zip_file()

    with printer.Do("Deleting old configuration files"):
        for ovpn_dir in ("ovpn_udp", "ovpn_tcp"):
            remove_dir = "{}/{}".format(zip_dir, ovpn_dir)
            if os.path.exists(remove_dir):
                rmtree(remove_dir, ignore_errors=True)

    with ZipFile(zip_file, "r") as zip_stream:
        name_list = zip_stream.namelist()

        with printer.incremental_bar(
            "Unzipping '{}'".format(os.path.basename(zip_file)), max=len(name_list)
        ) as incremental_bar:
            for file_name in name_list:
                zip_stream.extract(file_name, zip_dir)
                incremental_bar.next()


def update(force=False):
    """Update the nordvpn configuration files
    """

    printer = Printer()
    if force:
        get()
        unzip()
    else:
        zip_file = resources.get_zip_path()
        orig_file = resources.get_zip_path("ovpn.zip.orig")
        if update_needed():
            get()
            if not file_equals(orig_file, zip_file):
                unzip()
            else:
                printer.info(zip_file + " already up-to-date")
        else:
            next_update = datetime.fromtimestamp(os.path.getctime(zip_file)) + TIMEOUT
            printer.info(
                "No update needed. Next necesseray update needed at {!s}".format(
                    next_update
                )
            )

    areas.update_database()
    return True


def update_needed():
    """Check if an update is needed
    : returns: False if the zip file's creation time hasn't reached the timeout
               else True.
    """
    try:
        zip_file = resources.get_zip_file()
        now = datetime.now()
        time_created = datetime.fromtimestamp(os.path.getctime(zip_file))
        return now - TIMEOUT > time_created
    except resources.ResourceNotFoundError:
        return True
