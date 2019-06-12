#!/usr/bin/env python

import time
from connord import connect
from main_test_module import get_servers_stub, measure_time

ping_output_fixture_good = b"""PING archlinux.org (192.168.8.1) 56(84) bytes of data.

--- archlinux.org ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 9ms
rtt min/avg/max/mdev = 0.895/0.980/1.040/0.067 ms
"""

ping_output_fixture_bad = b"""PING archlinux.org (192.168.8.1) 56(84) bytes of data.

--- archlinux.org ping statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 9ms
"""


def test_ping(mocker):
    test_server = {}
    test_server["ip_address"] = "100.100.100.100"

    mocked_popen = mocker.patch("connord.connect.subprocess.Popen")
    process_mock = mocker.MagicMock()
    attrs = {"communicate.return_value": (ping_output_fixture_good, b"error")}
    process_mock.configure_mock(**attrs)
    mocked_popen.return_value.__enter__.return_value = process_mock

    server = connect.ping(test_server)

    mocked_popen.assert_called()
    assert server["ping"] == 0.980


def test_ping_bad(mocker):
    test_server = {}
    test_server["ip_address"] = "100.100.100.100"

    mocked_popen = mocker.patch("connord.connect.subprocess.Popen")
    process_mock = mocker.MagicMock()
    attrs = {"communicate.return_value": (ping_output_fixture_bad, b"error")}
    process_mock.configure_mock(**attrs)
    mocked_popen.return_value.__enter__.return_value = process_mock

    server = connect.ping(test_server)

    mocked_popen.assert_called()
    assert server["ping"] is None


def test_ping_servers_parallelness(mocker):
    test_server = {}
    test_server["ip_address"] = "100.100.100.100"

    def ping_fix(ip):
        time.sleep(0.2)
        return test_server

    mocker.patch("connord.connect.ping", ping_fix)
    servers_ = get_servers_stub()
    actual_servers = connect.ping_servers_parallel(servers_)
    expected_servers = []
    for i in range(len(servers_)):
        expected_servers.append(test_server)

    assert actual_servers == expected_servers
