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

import sys
from progress.bar import IncrementalBar


class ConnordError(Exception):
    """Main Exception class for connord module"""


# pylint: disable=too-few-public-methods
class Borg:
    """Define a borg class"""

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Printer(Borg):
    """Generic printer. Every intentional output must go through this printer
    to recognize quiet and verbose mode set on the command-line or in the
    configuration.
    """

    def __init__(self, verbose=False, quiet=False):
        """Initialize the printer. The attributes don't change once they are set.

        :param verbose: if True print info messages
        :param quiet: if True suppress error and info messages
        """

        Borg.__init__(self)
        if "verbose" not in self.__dict__.keys():
            self.verbose = verbose
        if "quiet" not in self.__dict__.keys():
            self.quiet = quiet

    def error(self, error):
        """Prints errors if not quiet"""
        if not self.quiet:
            print(error, file=sys.stderr)

    def info(self, info):
        """Prints info messages if verbose"""
        if self.verbose and not self.quiet:
            print(info)

    @staticmethod
    def write(message):
        """Prints messages independently from verbose and quiet settings
        There's no need to call this function directly. Just pass Printer to the
        file attribute of the __builtin__ print method.

        Example: print('something', file=Printer())
        """
        print(message, end="")

    def incremental_bar(self, message="", **kwargs):
        """Return an Incremental bar if verbose else a NullBar(IncrementalBar)
        which does nothing but can be used like the usual IncrementalBar

        :param message: the prefix message
        :param kwargs: kwargs to pass through to the IncrementalBar
        :returns: IncrementalBar if verbose else NullBar
        """
        if self.verbose:
            return IncrementalBar(message, **kwargs)

        return self.NullBar()

    class NullBar(IncrementalBar):
        """Fake an IncrementalBar doing nothing"""

        # pylint: disable=super-init-not-called
        def __init__(self, message="", **kwargs):
            pass

        def start(self):
            pass

        def update(self):
            pass

        def show(self, *args, **kwargs):
            pass

        def next(self, n=1):
            pass

        def write(self, s):
            pass

        def finish(self):
            pass


# TODO: Introduce ValidationError to be used verifying command-line arguments
# in filters


__version__ = "0.1.2"
__license__ = "GNU General Public License v3 or later (GPLv3+)"
__copyright__ = """connord  Copyright (C) 2019  Mael Stor <maelstor@posteo.de>
This program comes with ABSOLUTELY NO WARRANTY; This is free software, and you
are welcome to redistribute it under certain conditions; See the LICENSE file
shipped with this software for details."""
