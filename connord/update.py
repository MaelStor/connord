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
from connord import areas

__URL = "https://downloads.nordcdn.com/configs/archives/servers"
__ARCHIVES = {"standard": "ovpn.zip", "obfuscated": "ovpn_xor.zip"}
TIMEOUT = timedelta(hours=1)


class UpdateError(ConnordError):
    """Raised during update"""


def update_orig(archive):
    """
    Move the original file to make room for the newly downloaded file
    """

    try:
        zip_file = resources.get_zip_file(zip_name=archive, create_dirs=True)
    except resources.ResourceNotFoundError:
        return False

    move(zip_file, zip_file + ".orig")
    return True


def get():
    """Get the zip file
    """

    for category, archive in __ARCHIVES.items():
        printer = Printer()
        zip_path = resources.get_zip_path(archive)
        update_orig(archive)
        spinner = printer.spinner("Downloading {} configurations".format(category))
        url = "{}/{}".format(__URL, archive)
        with requests.get(url, stream=True, timeout=1) as response, open(
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

    with printer.Do("Deleting old configuration files"):
        for ovpn_dir in ("ovpn_udp", "ovpn_tcp"):
            remove_dir = "{}/{}".format(zip_dir, ovpn_dir)
            if os.path.exists(remove_dir):
                rmtree(remove_dir, ignore_errors=True)

    for key, archive in __ARCHIVES.items():
        zip_file = resources.get_zip_file(archive)
        with ZipFile(zip_file, "r") as zip_stream:
            name_list = zip_stream.namelist()

            with printer.incremental_bar(
                "Unzipping {} configurations".format(key), max=len(name_list)
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
        update_archives = False
        for archive in __ARCHIVES.values():
            zip_file = resources.get_zip_path(archive)
            # if one archive needs an update all archives are updated
            if update_needed(zip_file):
                update_archives = True
                break
        else:
            raise UpdateError(
                "Just one update per hour allowed. Use --force to ignore "
                "the timeout."
            )

        if update_archives:
            get()
            for archive in __ARCHIVES.values():
                zip_file = resources.get_zip_path(archive)
                orig_file = resources.get_zip_path(archive + ".orig")
                if not file_equals(orig_file, zip_file):
                    unzip()
                    break
            else:
                printer.info("Configurations are up-to-date.")

    areas.update_database()
    return True


def update_needed(zip_path):
    """Check if an update is needed
    : returns: False if the zip file's creation time hasn't reached the timeout
               else True.
    """
    now = datetime.now()
    time_created = datetime.fromtimestamp(os.path.getctime(zip_path))
    return now - TIMEOUT > time_created
