#!/usr/bin/env python
"""Main test module to define common functions"""

import json
import functools
import time


def _get_stub(stub):
    with open("tests/fixtures/" + stub) as file_handle:
        return file_handle.read()


def _get_servers_stub():
    with open("tests/fixtures/servers_stub.json") as json_file:
        return json.load(json_file)


def _get_expected_servers_by_id(ids):
    servers_stub = _get_servers_stub()
    expected_servers = []
    for server_id in ids:
        for server in servers_stub:
            if server["id"] == server_id:
                expected_servers.append(server)

    return expected_servers


def _get_expected_servers_by_domain(domains):
    servers_stub = _get_servers_stub()
    expected_servers = []
    for domain in domains:
        for server in servers_stub:
            if server["domain"] == domain + ".nordvpn.com":
                expected_servers.append(server)

    return expected_servers


def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        time_needed = (start - end) * 1000
        print("{!r}  {:2.2} ms".format(func.__name__, time_needed))
        return result

    return wrapper
