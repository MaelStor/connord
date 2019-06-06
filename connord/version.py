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

"""
Everything around version
"""

from connord import __version__

__COPYRIGHT = """connord  Copyright (C) 2019  Mael Stor <maelstor@posteo.de>
This program comes with ABSOLUTELY NO WARRANTY; This is free software, and you
are welcome to redistribute it under certain conditions; See the LICENSE file
shipped with this software for details."""


# TODO: Rename to show()
def print_version():
    """Prints the version of connord
    """
    # TODO: Show config in use along with the version
    print("connord", __version__)
    print(__COPYRIGHT)
