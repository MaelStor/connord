#!/usr/bin/env bash

# shellcheck disable=2034,2181

this_dir="$(dirname "$0")"

dest_dir="$(readlink -e "${this_dir}/../tmp/")"
mkdir -p "$dest_dir"
dest_path="${dest_dir}/openvpn_ipchange.output"

trap cleanup EXIT

cleanup() {
  [[ "$dest_path" ]] && rm -f "$dest_path"
}

# setup
foreign_option_1="redirect-gateway def1"
foreign_option_2="dhcp-option DNS 103.86.96.100"
foreign_option_3="dhcp-option DNS 103.86.99.100"
foreign_option_4="sndbuf 555555"
foreign_option_5="rcvbuf 555555"
foreign_option_6="explicit-exit-notify"
foreign_option_7="comp-lzo no"
foreign_option_8="route-gateway 10.8.9.1"
foreign_option_9="topology subnet"
foreign_option_10="ping 120"
foreign_option_11="ifconfig 10.8.9.15 255.255.255.0"
foreign_option_12="cipher AES-256-GCM"
foreign_option_13="dhcp-option SEARCH google.com"

dev='tun0'
script_type='ipchange'

# run
# shellcheck disable=1090
source "${this_dir}/../../connord/scripts/openvpn_ipchange.bash" "$dest_path" '[AF_INET]111.111.111.111 1194'
(($? == 0)) || exit 1

# test if file exists
readlink -e "$dest_path" || exit 1

# test if output is valid yaml
python - << EOF
import yaml
with open('$dest_path') as fd:
  assert bool(yaml.safe_load(fd))
EOF
