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
Prints the version along with the copyright.
"""

from connord import __version__, __copyright__, Printer
from connord import resources


def print_version():
    """Prints the version of connord along with the copyright.
    """
    printer = Printer()
    print("connord {}".format(__version__), file=printer)
    print(__copyright__, file=printer)
    printer.info("\nConfiguration directory: '{}'".format(resources.get_config_dir()))
