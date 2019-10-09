#!/usr/bin/env python
"""Main test module to define common functions"""

import json
import functools
import time


def get_stub(stub):
    with open("tests/fixtures/" + stub) as file_handle:
        return file_handle.read()


def get_stub_file(stub):
    return "tests/fixtures/" + stub


def get_json(fixture):
    with open("tests/fixtures/" + fixture) as file_handle:
        return json.load(file_handle)


def get_servers_stub():
    with open("tests/fixtures/servers_stub.json") as json_file:
        return json.load(json_file)


def get_expected_servers_by_id(ids):
    servers_stub = get_servers_stub()
    expected_servers = []
    for server_id in ids:
        for server in servers_stub:
            if server["id"] == server_id:
                expected_servers.append(server)

    return expected_servers


def get_expected_servers_by_domain(domains):
    servers_stub = get_servers_stub()
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


class MockBase:
    def __init__(self, module_under_test):
        self.module_under_test = module_under_test

    def _get_base_mock(self, module_s):
        return "connord." + self.module_under_test + "." + module_s

    def mock_os_any(self, mocker, func, return_value):
        if func:
            basemock = self._get_base_mock("os." + func)
            return mocker.patch(basemock, return_value=return_value)

        basemock = self._get_base_mock("os")
        return mocker.patch(basemock)

    def mock_os(self, mocker):
        basemock = self._get_base_mock("os")
        return mocker.patch(basemock)

    def mock_open(self, mocker):
        basemock = self._get_base_mock("open")
        return mocker.patch(basemock, mocker.mock_open(), create=True)

    def setup(self, module, create_tmpdir=False):
        import importlib

        importlib.reload(module)
        if create_tmpdir:
            self.create_tmpdir()

    def create_tmpdir(self):
        import os

        tempdir = "tests/tmp/" + self.module_under_test

        os.makedirs(tempdir, exist_ok=True)

    def get_tmpdir(self):
        return "tests/tmp/" + self.module_under_test

    def tear_down(self):
        from os import path
        from shutil import rmtree

        tempdir = "tests/tmp/" + self.module_under_test
        if path.exists(tempdir):
            rmtree(tempdir)

    def mock_user_is_root(self, mocker, return_value):
        basemock = self._get_base_mock("user.is_root")
        return mocker.patch(basemock, return_value=return_value)

    def mock_resource_filename(self, mocker, return_value):
        basemock = self._get_base_mock("resource_filename")
        return mocker.patch(basemock, return_value=return_value)
