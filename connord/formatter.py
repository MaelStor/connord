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


class Formatter():
    """Basic formatter"""

    def __init__(self, output=None, max_line_length=80):
        self.max_line_length = max_line_length
        if output:
            self.output = output
        else:
            self.output = ''

    def format_ruler(self, sep="="):
        return sep * self.max_line_length

    def center_string(self, string, sep=" "):
        left = (self.max_line_length - len(string) - 2) // 2
        right = self.max_line_length - left - len(string) - 2
        return "{} {} {}".format(left * sep, string, right * sep)

    def write(self, string):
        self.output += string

    def get_output(self, rstrip=True):
        if rstrip:
            return self.output.rstrip()

        return self.output
