<h1 align="center">C&#xF8;nN&#xF8;rD</h1>
<h2 align="center">Connect to NordVPN servers secure and fast</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square"></a>
<a href="https://choosealicense.com/licenses/gpl-3.0/"><img alt="License" src="https://img.shields.io/badge/license-GPL--3.0--or--later-green.svg?style=flat-square"></a>
<a href="https://docs.python.org/"><img alt="Python Version" src="https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg?style=flat-square"></a>
<a href="https://github.com/MaelStor/connord"><img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/MaelStor/connord.svg?style=flat-square"></a>
<a href="https://travis-ci.com/MaelStor/connord/"><img alt="Travis (.com) branch"
src="https://img.shields.io/travis/com/MaelStor/connord/master.svg?style=flat-square"></a>
</p>
----

C&#xF8;nN&#xF8;rD is a tool to connect to NordVPN servers and manages DNS through 
resolvconf and the firewall through IPTables to keep your connection secure. It is
developed with safety and fast processing in mind.

Loading profiles for the firewall is fully supported. You can define rules and
fallback files for iptables in YAML format and Jinja2 templating. It's totally 
up to you, how you configure your firewall. Defaults are provided for unexperienced
users who just want to surf the web but can be easily modified to any complexity.

You can select servers
by country, city, load, categories and features provided by NordVPN. UDP is the default
protocol but can be changed to TCP in the configuration or command-line. The default configuration can be
changed in /etc/connord/config.yml or in site-packages/connord/config/config.yml when installed through pip.

----
*Not implemented yet*

The systemd service tries to reconnect if 
the connection is dead and can be configured to switch on a time basis or when 
load is reaching the max\_load variable. The interval to check these values can
be configured with check\_interval. This feature is implemented using a systemd 
timer. The servers are automatically updated by the service or manually through 
the cli.

----

C&#xF8;nN&#xF8;rD tries hard to be compatible to the OpenVPN tool, so
files are stored in OpenVPN directories per default. C&#xF8;nN&#xF8;rD can also be started in
daemon mode.


## Dependencies
* python3
* resolvconf
* iptables
* systemd
* openvpn

## Installation
First make sure you have all dependencies installed.

#### Ubuntu/Debian

    apt-get install python3 resolvconf iptables systemd openvpn

#### Arch

    pacman -Sy python openresolv iptables systemd openvpn

Installation of C&#xF8;nN&#xF8;rD

    pip install --upgrade connord

or clone the repo

    git clone git@github.com:MaelStor/connord.git
    cd connord

and install in userspace with

    pip install --user .

or globally with

    sudo pip install .

## Supported Commandline Options

Commandline options overwrite the configuration.

#### Main options
<pre>
usage: connord [-h] [-q | -v] {update,list,connect,kill,iptables,version} ...

connord is a script/service to connect to nordvpn servers. It manages dns
through resolvconf and the firewall through iptables to keep your connection
safe.

positional arguments:
  {update,list,connect,kill,iptables,version}
    update              Update nordvpn configuration files.
    list                Prints all servers if no argument is given.
    connect             Connect to a server.
    kill                Kill all processes of connord. Useful in daemon mode.
    iptables            Wrapper around iptables.
    version             Show version

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Be quiet
  -v, --verbose         Be verbose
</pre>

#### Listings
<pre>
usage: connord list [-h] [-c [COUNTRY]] [-a [AREA]] [-f [FEATURE]] [-t [TYPE]]
                    [--netflix]
                    [--max-load MAX_LOAD | --min-load MIN_LOAD | --load LOAD]
                    [--top TOP] [--iptables]

optional arguments:
  -h, --help            show this help message and exit
  -c [COUNTRY], --country [COUNTRY]
                        select a specific country. may be specified multiple
                        times. if one of these arguments has no specifier then
                        all country codes are printed.
  Not implemented yet -a [AREA], --area [AREA]
                        select a specific area.may be specified multiple
                        times. if one of these arguments has no specifier then
                        all areas are printed.
  -f [FEATURE], --feature [FEATURE]
                        select servers with a specific list of features. may
                        be specified multiple times. if one of these arguments
                        has no specifier then all possible features are
                        printed.
  -t [TYPE], --type [TYPE]
                        select servers with a specific type. may be specified
                        multiple times. if one of these arguments has no
                        specifier then all possible types are printed.
  --netflix             Select servers configured for netflix.
  --max-load MAX_LOAD   Filter servers by maximum load.
  --min-load MIN_LOAD   Filter servers by minimum load.
  --load LOAD           Filter servers by exact load match.
  --top TOP             Show TOP count resulting servers.
  --iptables            List all rules in iptables
</pre>

#### Update
<pre>
usage: connord update [-h] [-f]

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  Force update no matter of configuration.
</pre>

#### Connect
<pre>
usage: connord connect [-h] [-s SERVER | -b] [-c [COUNTRY]] [-a [AREA]]
                       [-f [FEATURE]] [-t [TYPE]] [--netflix]
                       [--max-load MAX_LOAD | --min-load MIN_LOAD | --load LOAD]
                       [-d] [-i [CONFIG]] [-o OPENVPN_OPTIONS] [--udp | --tcp]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Connect to a specific server. Arguments -c, -a, -f, -t
                        have no effect.
  -b, --best            Use best server depending on server load. When
                        multiple servers got the same load use the one with
                        the best ping.
  -c [COUNTRY], --country [COUNTRY]
                        Select a specific country. May be specified multiple
                        times.
   Not implemented yet -a [AREA], --area [AREA]
                        Select a specific area. May be specified multiple
                        times.
  -f [FEATURE], --feature [FEATURE]
                        Select servers with a specific list of features. May
                        be specified multiple times.
  -t [TYPE], --type [TYPE]
                        Select servers with a specific type. May be specified
                        multiple times.
  --netflix             Select servers configured for netflix.
  --max-load MAX_LOAD   Filter servers by maximum load.
  --min-load MIN_LOAD   Filter servers by minimum load.
  --load LOAD           Filter servers by exact load match.
  -d, --daemon          Start in daemon mode.
  Not implemented yet -i [CONFIG], --config [CONFIG]
                        Take config from /path/to/config.{yml|ini}.
  -o OPENVPN_OPTIONS, --openvpn OPENVPN_OPTIONS
                        Options to pass through to openvpn as single string
  --udp                 Use UDP protocol. This is the default
  --tcp                 Use TCP protocol. Only one of --udp or --tcp may be
                        present.
</pre>

#### Show version
<pre>
usage: connord version [-h]

optional arguments:
  -h, --help  show this help message and exit
</pre>

#### Kill running connord processes
*Not implemented yet*

<pre>
usage: connord kill [-h]

optional arguments:
  -h, --help  show this help message and exit
</pre>

#### Manage IPTables
<pre>
usage: connord iptables [-h] {reload,flush,apply} ...

positional arguments:
  {reload,flush,apply}
    reload              Reload iptables
    flush               Flush iptables
    apply               Apply iptables rules defined in configuration

optional arguments:
  -h, --help            show this help message and exit
</pre>

###### Iptables apply
<pre>
usage: connord iptables apply [-h] [--udp | --tcp] domain

positional arguments:
  domain      Apply iptables rules with domain

optional arguments:
  -h, --help  show this help message and exit
  --udp       Use UDP protocol. This is the default
  --tcp       Use TCP protocol. Only one of --udp or --tcp may be present
</pre>

###### Iptables reload
Reload iptables rules with current configured server after editing them.

###### Iptables flush
Flush all tables

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
obfuscated                Obfuscated Servers
onion                     Onion Over VPN
</pre>

## Configuration

*Not implemented yet*
Possible values:
<pre>
update_interval     accepts seconds, minutes, hours, days, months, years. 
                    Format as string for example 'days=1' is the default. If 
                    any value is set to 0 there's always an update.
</pre>

## Developing

Clone the repo and install development environment:

    git clone git@github.com:MaelStor/connord.git
    cd connord
    make develop

You're good to go from here :)

## TODO

* [ ] Improve code documentation
* [ ] Implement different output formats for listings. --pretty --terse --json.
* [ ] Offer a sorting option to sort the output by different keys.
* [X] Filter by max-load, load and min-load
* [ ] Filter by max-domain-number, cidr
* [ ] Offer option to just show --top $number results
* [ ] Offer option save current location in latitude, long to calculate shortest
      distance to servers. 
* [ ] Colorize output if wanted. Load >70 in red 30-69 yellow and rest green. Do
      offer color=always,auto (respects pipes),never.
* [ ] create links for openvpn in /etc/openvpn/client to actual configuration 
      files in nordvpn/
* [ ] Bash completion
* [ ] Zsh completion
