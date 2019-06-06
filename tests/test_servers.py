#!/usr/bin/env python

from connord import servers
from main_test_module import _get_servers_stub


def test_get_servers(requests_mock):
    _servers = _get_servers_stub()
    _url = "https://api.nordvpn.com/server"
    expected_useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) \
Gecko/20100101 Firefox/60.0"
    header = {"User-Agent": expected_useragent}

    requests_mock.get(_url, headers=header, json=_servers)

    actual_servers = servers.get_servers()
    actual_useragent = requests_mock.last_request.headers["User-Agent"]
    actual_url = requests_mock.last_request.url
    assert actual_servers == _servers
    assert actual_url == _url
    assert actual_useragent == expected_useragent


def test_to_string():
    # test with server stub
    _servers = _get_servers_stub()

    with open("tests/fixtures/servers_stub_to_string.txt") as file_handle:
        # use rstrip to strip the final newline which wasn't deletable from the
        # server_stub_to_string.txt file
        expected_string = file_handle.read().rstrip()

    actual_string = servers.to_string(_servers)
    assert actual_string == expected_string


def test_to_string_when_servers_is_empty():
    assert servers.to_string(list()) == str()
