<h1 align="center">C&#xF8;nN&#xF8;rD</h1>
<h2 align="center">Connect to NordVPN servers secure and fast</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square"></a>
<a href="https://choosealicense.com/licenses/gpl-3.0/"><img alt="License" src="https://img.shields.io/badge/license-GPL--3.0--or--later-green.svg?style=flat-square"></a>
<a href="https://docs.python.org/"><img alt="Python Version" src="https://img.shields.io/badge/python-3.6%20%7C%203.7-blue.svg?style=flat-square"></a>
<a href="https://github.com/MaelStor/connord"><img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/MaelStor/connord.svg?style=flat-square"></a>
<a href="https://travis-ci.com/MaelStor/connord/"><img alt="Travis (.com) branch" src="https://img.shields.io/travis/com/MaelStor/connord/master.svg?style=flat-square"></a>
<a href="https://github.com/MaelStor/connord"><img alt="Coveralls github" src="https://img.shields.io/coveralls/github/MaelStor/connord.svg?style=flat-square"></a>
</p>

---

C&#xF8;nN&#xF8;rD connects you to NordVPN servers with
[OpenVPN](https://openvpn.net/community-resources/#articles) and you can choose
between a high amount of possible filters, to make it easy for you to connect 
to servers with the best performance and features the server offers to you. 
It's taken care that your DNS isn't leaked. You can test your DNS spoofability
[here](https://www.grc.com/dns/dns.htm) and DNS leaks 
[here](https://ipleak.net/).

Most of the tools out there provide their own set of firewall rules without
possibility to customize them to your needs. Sometimes it is just cumbersome to
write your own set of rules and make them compatible with the connection tool.
C&#xF8;nN&#xF8;rD just provides a reasonable default, but you stay ALWAYS in
control of your firewall and can customize every rule to your needs. Furthermore
C&#xF8;nN&#xF8;rD exposes a lot of environment variables from OpenVPN and the
running connord instance to .rules and .fallback files so you can tailor each
rule dynamically to your interfaces, current ip addresses and more.
See the Iptables section on how it works or just accept the defaults, which work
perfectly fine for unexperienced users, without breaking your privacy and internet
experience.

C&#xF8;nN&#xF8;rD keeps configuration files in openvpn folders, so you can
always step back to OpenVPN if you like to without the need to search too much
around. You may keep C&#xF8;nN&#xF8;rD around then to update your configuration 
files with a cronjob on a regular basis and enjoy the nice server listings ;) 
But if you use this tool for connecting you can easily change every option that 
is set to start the OpenVPN process in a simple yaml configuration file, or 
just keep them that way if your glad with the defaults. Honestly the defaults 
should cover most use cases.

## Dependencies

- python3
- resolvconf
- iptables
- openvpn

## Quick start guide

- Follow Installation instructions below
- (Optional) Copy everything within your python `site-packages/connord/config/` folder
  to `/etc/connord`. For example python3.7:

  <pre>
      sudo cp -r /lib/python3.7/site-packages/connord/config /etc/connord
      sudoedit /etc/connord/config.yml
  </pre>

- (Optional) Customize `config.yml` either in `site-packages` or `/etc/connord` if
  you've taken the optional step above.
- Execute `$ sudo connord connect`

## Installation

First make sure you have all system dependencies installed.

#### Ubuntu/Debian

    $ sudo apt-get install python3 resolvconf iptables openvpn

#### Arch

    $ sudo pacman -Sy python openresolv iptables openvpn

#### Installation of C&#xF8;nN&#xF8;rD

    $ pip install --upgrade connord

or globally:

    $ sudo pip install --upgrade connord

You may also clone the repo

    $ git clone git@github.com:MaelStor/connord.git
    $ cd connord

and install in userspace with

    $ pip install --user .

or globally with

    $ sudo pip install .

## General section

C&#xF8;nN&#xF8;rD per default doesn't output anything on stdout and behaves like
any other standard command-line tool. If you experience problems running 
connord, try the same command in verbose mode
 with

    connord -v COMMAND

or

    connord --verbose COMMAND

for debugging purposes. You should see in most cases where the error occurred. 
There may be still hard to track bugs, please report them to the Issue board on 
[Github](https://github.com/MaelStor/connord/issues).

Error messages are written to stderr in your shell. You can suppress error 
messages with `-q` or `--quiet` if you like to.

Verbose mode of `openvpn` can be set in `config.yml` in the openvpn
section or at the command-line when using `connord connect` adding it to the
openvpn command with `-o '--verb 3'`.

## Configuration

Default configuration files are located in your python
`site-packages/connord/config` folder. You may wish to create an more permanent
location and copy them to `/etc/connord/`. The folder needs to be created if not
already done. Configuration files in site-packages don't survive an upgrade in
contrast to `/etc/connord`. If the `/etc/connord` folder exists no configuration
files in `site-packages` are read.

To see which configuration folder is active run `connord --verbose version`.

#### config.yml

The main configuration file in [YAML](https://yaml.org/) format. Every variable
set here is exposed to .rules and .fallback templates.

###### iptables

So you may set something like this

<pre>
iptables
  dns:
    # NordVPN
    - '103.86.99.100/32'
    - '103.86.96.100/32'
</pre>

and use it for example in 01-filter.rules:

<pre>
OUTPUT:
  policy: ACCEPT
  action: None
  rules:
{% for server in iptables.dns %}
  - dst: "{{ server }}"
    protocol: udp
    udp:
      dport: '53'
    target: ACCEPT
{% endfor %}
</pre>

what creates the following after rendering:

<pre>
OUTPUT:
  policy: ACCEPT
  action: None
  rules:
  - dst: '103.86.99.100/32'
    protocol: udp
    udp:
      dport: '53'
    target: ACCEPT
  - dst: '103.86.96.100/32'
    protocol: udp
    udp:
      dport: '53'
    target: ACCEPT
</pre>

Like it? See more examples in the rules and fallback files section.

###### openvpn

These are the default settings to start OpenVPN:

<pre>
openvpn:
  daemon: False
  auth-user-pass: "built-in"
  auth-nocache: False
  auth-retry: "nointeract"
  down-pre: True
  redirect-gateway: True
  script-security: 2
  # This section is special to connord and can't be found in the openvpn manual
  scripts:
    - name: "up"
      path: "built-in"
      stage: "up"
      creates: "up.env"
    - name: "down"
      path: "built-in"
      stage: "down"
      creates: "down.env"
    - name: "ipchange"
      path: "built-in"
      stage: "always"
      creates: "ipchange.env"
</pre>

For an overview of all possible options see `$ man openvpn`. You just need to
strip off the leading '--' and place it somewhere in the openvpn section.
Arguments are written after `:` or if the option doesn't take any
arguments place `True` after `:`. Most common mistake is to ignore
indentation. But since this is a yaml file indentation IS important. Further
reading about [YAML Syntax](https://yaml.org/spec/1.1/spec.html). There's
the special keyword `built-in` around what can be applied to:

- auth-user-pass
- scripts paths
  - name: up
  - name: down
  - name: ipchange

if you like to use the built-in paths, what is the default behaviour. If you
don't like to run a script say when openvpn goes down delete or comment out

<pre>
    - name: "down"
      path: "built-in"
      stage: "down"
      creates: "down.env"
</pre>

## Iptables

#### rules and fallback files

These files are [jinja2](http://jinja.pocoo.org/docs/2.10/) templates which are
rendered with the `config.yml` file and .env files created by the built-in `up`,
`down` and `ipchange` scripts when openvpn starts running.

###### Naming scheme

The naming scheme is important. Let's take for example the rules file
which shall be applied to netfilters `filter` table. `01-filter.rules`.
The leading number isn't necessary but you can control the order when to apply
the files that way. After the dash `-` follows the table name. The dash isn't
needed when there is no leading number.
The suffix `.rules` causes the rules to be applied after successfully
establishing a connection to a server. The suffix `.fallback` causes the rules to be applied when disconnecting from a server or
after invokation of `connord iptables flush`. If you're writing ipv6 rules for
the `filter` table place them in a file like `01-filter6.rules` or
`01-filter6.fallback`. Files with a `6` suffix are applied to ip6tables.

#### Variables

Every variable you define or is already defined in `config.yml` is available in
rules and fallback files. In addition to that the connord instance exposes the
following variables to `.rules` and `.fallback` files:

<pre>
vpn_remote      # the remote server ip address
vpn_protocol    # the protocol in use: udp or tcp
vpn_port        # may be 1194 (udp) or 443 (tcp)

gateway:
  ip_address    # the ip_address of the default gateway 
  interface     # the interface of the default gateway

lan:            # derived from the default gateway's interface
  inet:         # short for AF_INET
  - addr:       # the ip address of your LAN
    netmask:    # the netmask for your LAN
    broadcast:  # the broadcast address of your ipv4 LAN
  inet6:        # actually derived from AF_INET6
  - addr:       # (mostly one of) the ipv6 addressess
    netmask:    # the netmask for you LAN
  link:         # short for AF_LINK
  - addr:       # the MAC address of your LAN card
    broadcast:  # the broadcast address. Should be in most cases
                  ff:ff:ff:ff:ff:ff
</pre>

In `fallback` files `vpn_remote` is `0.0.0.0/0`, `vpn_protocol` is `udp` and
`vpn_port` is set to `1194`. Be aware that there can be more than one `inet` or
`inet6` addresses.

Variables exposed from OpenVPN scripts can be seen when starting connord
not in daemon mode. The list given here may be incomplete or too exhaustive for
your network and is therfor just an incomplete overview. Look at the output of 
connord for your environment.

<pre>
connord 'ipchange' enviroment variables: '/var/run/connord/ipchange.env'
ipchange_args:
  - '[AF_INET]100.100.100.100 1194'
  - '/var/run/connord/ipchange.env'
ip_address: '100.100.100.100'
port_number: '1194'
trusted_ip: '100.100.100.100'
trusted_port: '1194'
untrusted_ip: '100.100.100.100'
untrusted_port: '1194'
</pre>

<pre>
connord 'up' enviroment variables: '/var/run/connord/up.env'
up_args:
  - 'init'
  - '255.255.255.0'
  - '10.8.1.10'
  - '1590'
  - '1500'
  - 'tun1'
  - '/var/run/connord/up.env'
dhcp_option:
  dns:
    - '103.86.99.100'
    - '103.86.96.100'
dev: 'tun1'
ifconfig_broadcast: '10.8.1.255'
ifconfig_local: '10.8.1.10'
ifconfig_netmask: '255.255.255.0'
link_mtu: '1590'
route_net_gateway: '200.200.200.200'
route_vpn_gateway: '10.8.1.1'
script_context: 'init'
tun_mtu: '1500'
trusted_ip: '100.100.100.100'
trusted_port: '1194'
untrusted_ip: '100.100.100.100'
untrusted_port: '1194'
</pre>

<pre>
connord 'down' enviroment variables: '/var/run/connord/down.env'
down_args:
  - 'init'
  - '255.255.255.0'
  - '10.8.1.10'
  - '1590'
  - '1500'
  - 'tun1'
  - '/var/run/connord/down.env'
dhcp_option:
  dns:
    - '103.86.99.100'
    - '103.86.96.100'
dev: 'tun1'
ifconfig_broadcast: '10.8.1.255'
ifconfig_local: '10.8.1.10'
ifconfig_netmask: '255.255.255.0'
link_mtu: '1590'
route_net_gateway: '200.200.200.200'
route_vpn_gateway: '10.8.1.1'
script_context: 'init'
tun_mtu: '1500'
trusted_ip: '100.100.100.100'
trusted_port: '1194'
untrusted_ip: '100.100.100.100'
untrusted_port: '1194'
redirect_gateway: '1'
</pre>

Variables from OpenVPN scripts are only available in `.rules` files!

## Overview over the most important command-line options

Command-line options overwrite the configuration in `config.yml`

#### Main options

<pre>
usage: connord [-h] [-q | -v] {update,list,connect,kill,iptables,version} ...

CønNørD connects you to NordVPN servers with OpenVPN (https://openvpn.net) and
you can choose between a high amount of possible filters, to make it easy for
you to connect to servers with the best performance and features the server
offers to you. It's taken care that your DNS isn't leaked.

positional arguments:
  {update,list,connect,kill,iptables,version}
    update              Update nordvpn configuration files and the location
                        database.
    list                List features, types, ... and servers.
    connect             Connect to a server.
    kill                Kill the openvpn process.
    iptables            Manage iptables.
    version             Show version

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Suppress error messages.
  -v, --verbose         Show what's going.

Run a command with -h or --help for more information.
</pre>

#### Listings

<pre>
usage: connord list [-h] {iptables,countries,areas,features,types,servers} ...

The 'list' command allows some powerful filtering so you can select a server
tailored to your demands. 'types', 'features', 'areas', 'countries' give you
an overview output of possible arguments to the respective flag.

positional arguments:
  {iptables,countries,areas,features,types,servers}
    iptables            List rules in netfilter tables. With no arguments list
                        ipv4 'filter' table.
    countries           List all countries with NordVPN servers.
    areas               List all areas/cities with NordVPN servers.
    features            List all possible features of NordVPN servers.
    types               List all possible types/categories of NordVPN servers.
    servers             List servers filtered by specified arguments.

optional arguments:
  -h, --help            show this help message and exit

Run a command with -h or --help for more information.
</pre>

###### servers

<pre>
usage: connord list servers [-h] [-c COUNTRY] [-a AREA] [-f FEATURE] [-t TYPE]
                            [--netflix]
                            [--max-load MAX_LOAD | --min-load MIN_LOAD | --load LOAD]
                            [--top TOP]

List servers filtered by one or more of the specified arguments. If no
arguments are given list all NordVPN servers. To see possible values for
--area, --country, --feature and --type have a look at the respective 'list'
commands.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNTRY, --country COUNTRY
                        Select a specific country. May be specified multiple
                        times.
  -a AREA, --area AREA  Select a specific area. May be specified multiple
                        times.
  -f FEATURE, --feature FEATURE
                        Select servers with a specific list of features. May
                        be specified multiple times.
  -t TYPE, --type TYPE  Select servers with a specific type. May be specified
                        multiple times.
  --netflix             Select servers configured for netflix.
  --max-load MAX_LOAD   Filter servers by maximum load.
  --min-load MIN_LOAD   Filter servers by minimum load.
  --load LOAD           Filter servers by exact load match.
  --top TOP             Show TOP count resulting servers.
</pre>

#### Update NordVPN server configuration files and the location database

<pre>
usage: connord update [-h] [-f]

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  Force update no matter of configuration.
</pre>

#### Connect to NordVPN servers

<pre>
usage: connord connect [-h] [-s SERVER | -b] [-c COUNTRY] [-a AREA]
                       [-f FEATURE] [-t TYPE] [--netflix]
                       [--max-load MAX_LOAD | --min-load MIN_LOAD | --load LOAD]
                       [-d] [-o OPENVPN_OPTIONS] [--udp | --tcp]

Connect to NordVPN servers. You may specify a single server of your choice
with -s SERVER, where SERVER is a COUNTRY_CODE followed by a number. This must
be a SERVER for which a configuration file exists. The same filters --area,
--country ... like in the 'list' command can be applied here. For a list of
possible values see the respective command in the 'list' command. IMPORTANT:
Note that currently obfuscated servers aren't supported.

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Connect to a specific server. Only -d, -o, --udp and
                        --tcp have an effect.
  -b, --best            Use best server depending on server load. When
                        multiple servers got the same load use the one with
                        the best ping. This is the default behaviour if not
                        specified on the command-line
  -c COUNTRY, --country COUNTRY
                        Select a specific country. May be specified multiple
                        times.
  -a AREA, --area AREA  Select a specific area. May be specified multiple
                        times.
  -f FEATURE, --feature FEATURE
                        Select servers with a specific feature. May be
                        specified multiple times.
  -t TYPE, --type TYPE  Select servers with a specific type. May be specified
                        multiple times.
  --netflix             Select servers configured for netflix.
  --max-load MAX_LOAD   Filter servers by maximum load.
  --min-load MIN_LOAD   Filter servers by minimum load.
  --load LOAD           Filter servers by exact load match.
  -d, --daemon          Start in daemon mode.
  -o OPENVPN_OPTIONS, --openvpn OPENVPN_OPTIONS
                        Options to pass through to openvpn as single string
  --udp                 Use UDP protocol. This is the default
  --tcp                 Use TCP protocol. Only one of --udp or --tcp may be
                        present.
</pre>

#### Manage IPTables

<pre>
usage: connord iptables [-h] {list,reload,flush,apply} ...

Manage your iptables configuration with this command. Under normal
cirumstances your rules files are automatically applied when running
'connect'. If somethings going wrong or you are modifying rules you can try
one of the commands defined here. You can list your current iptables rules
with the 'list' command as an alternative to the native iptables -L -vn
--line-num.

positional arguments:
  {list,reload,flush,apply}
    reload              Reload iptables configuration.
    flush               Flush iptables.
    apply               Apply iptables rules per 'table'.

optional arguments:
  -h, --help            show this help message and exit

Run a command with -h or --help for more information.
</pre>

## Supported FEATUREs:

<pre>
ikev2                     IKEv2/IPSec Protocol
openvpn_udp               UDP
openvpn_tcp               TCP
socks                     Socks 5
proxy                     HTTP Proxy
pptp                      PPTP
l2tp                      L2TP/IPSec
openvpn_xor_udp           OpenVPN UDP Obfuscated
openvpn_xor_tcp           OpenVPN TCP Obfuscated
proxy_cybersec            HTTP Proxy CyberSec
proxy_ssl                 HTTP Proxy (SSL)
proxy_ssl_cybersec        HTTP CyberSec Proxy (SSL)
ikev2_v6                  IKEv2/IPSec IPv6
openvpn_udp_v6            UDPv6
openvpn_tcp_v6            TCPv6
wireguard_udp             WireGuard UDP
openvpn_udp_tls_crypt     UDP TLS encryption
openvpn_tcp_tls_crypt     TCP TLS encryption
</pre>

## Supported TYPEs:

<pre>
double                    Double VPN
dedicated                 Dedicated IP
standard                  Standard VPN servers
p2p                       P2P
onion                     Onion Over VPN
</pre>


## Developing

Clone the repo and install the development environment:

    $ git clone git@github.com:MaelStor/connord.git
    $ cd connord
    $ make venv
    $ . .venv/bin/activate

You should be good to go from here. If you already have a virtualenv for connord
then executing `make develop` is sufficient.
