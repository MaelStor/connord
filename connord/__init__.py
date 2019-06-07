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
Init file
"""

import os


class ConnordError(Exception):
    """Main Exception class for connord module"""


# TODO: Introduce VerificationError to be used verifying commandline arguments
# in filters


__version__ = "0.1.0-alpha.2"
__license__ = "GNU General Public License v3 or later (GPLv3+)"
__basepath__ = os.path.dirname(os.path.abspath(__file__))
