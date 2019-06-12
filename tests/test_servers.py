#!/usr/bin/env python

from connord import servers
from main_test_module import get_servers_stub, get_stub


def test_get_servers(requests_mock):
    servers_ = get_servers_stub()
    url_ = "https://api.nordvpn.com/server"
    expected_useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) \
Gecko/20100101 Firefox/60.0"
    header = {"User-Agent": expected_useragent}

    requests_mock.get(url_, headers=header, json=servers_)

    actual_servers = servers.get_servers()
    actual_useragent = requests_mock.last_request.headers["User-Agent"]
    actual_url = requests_mock.last_request.url
    assert actual_servers == servers_
    assert actual_url == url_
    assert actual_useragent == expected_useragent


def test_to_string():
    # test with server stub
    servers_ = get_servers_stub()
    expected_string = get_stub("servers_stub_to_string.txt").rstrip()

    actual_string = servers.to_string(servers_)
    assert actual_string == expected_string


def test_to_string_when_servers_is_empty():
    assert servers.to_string(list()) == str()
