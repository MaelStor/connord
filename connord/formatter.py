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

"""Defines Formatter classes"""

from connord import Printer


class Formatter:
    """Basic formatter class"""

    def __init__(self, output=None, max_line_length=80):
        """Init

        :param output: if None set to ''. May be some leading output.
        :param max_line_length: Every calculation depends on the maximum column width
        """

        self.max_line_length = max_line_length
        self.output = output if output else ""

    def format_ruler(self, sep="="):
        """Returns a ruler with sep as fill with max_line_length as width."""
        return sep * self.max_line_length

    def center_string(self, string, sep=" "):
        """Return a string within sep as fill with max_line_length as width."""
        left = (self.max_line_length - len(string) - 2) // 2
        right = self.max_line_length - left - len(string) - 2
        return "{} {} {}".format(left * sep, string, right * sep)

    def write(self, string):
        """Append the string to the output. Must be named write to be compatible
        to the built-in print function.
        """
        self.output += string

    def get_output(self, rstrip=True):
        """Return the possibly stripped output collected so far"""
        if rstrip:
            return self.output.rstrip()

        return self.output

    def get_stream_file(self, stream=False):
        """Return self as stream if False else stdout"""
        return Printer() if stream else self
