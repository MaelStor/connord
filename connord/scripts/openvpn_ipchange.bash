#!/usr/bin/env bash
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

# shellcheck disable=SC2154
[[ "$script_type" ]] || exit 2

# shellcheck disable=2034,2021
[[ "$2" ]] && ip_address="$(echo "$2" | tr -d '[AF_INET]' | cut -d' ' -f1)"
# shellcheck disable=2034
[[ "$2" ]] && port_number="$(echo "$2" | cut -d' ' -f2)"

this_dir="$(dirname "${BASH_SOURCE[0]}")"
source "${this_dir}/dump_openvpn_env.bash"
