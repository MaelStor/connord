#!/usr/bin/env python

from connord.load import (
    LoadFilter,
    LoadError,
    MaxLoadFilter,
    MinLoadFilter,
    filter_servers,
)
from main_test_module import get_servers_stub, get_expected_servers_by_domain


def test_load_filter_when_load_is_valid():
    servers_ = get_servers_stub()

    domains = list()
    domains.append("de112")
    domains.append("de113")
    expected_servers = get_expected_servers_by_domain(domains)
    actual_servers = LoadFilter(servers_).apply(20)

    assert actual_servers == expected_servers


def test_load_filter_when_load_is_valid_should_not_throw_error():
    servers_ = get_servers_stub()

    try:
        actual_servers = LoadFilter(servers_).apply(0)
        assert isinstance(actual_servers, list)
    except LoadError:
        assert False

    try:
        actual_servers = LoadFilter(servers_).apply(1)
        assert isinstance(actual_servers, list)
    except LoadError:
        assert False

    try:
        actual_servers = LoadFilter(servers_).apply(50)
        assert isinstance(actual_servers, list)
    except LoadError:
        assert False

    try:
        actual_servers = LoadFilter(servers_).apply(99)
        assert isinstance(actual_servers, list)
    except LoadError:
        assert False

    try:
        actual_servers = LoadFilter(servers_).apply(100)
        assert isinstance(actual_servers, list)
    except LoadError:
        assert False


def test_load_filter_when_load_is_under_minimum():
    servers_ = get_servers_stub()

    try:
        LoadFilter(servers_).apply(-1)
        assert False
    except LoadError as error:
        assert str(error) == "Load must be >= 0 and <= 100."


def test_load_filter_when_load_is_over_maximum():
    servers_ = get_servers_stub()

    try:
        LoadFilter(servers_).apply(101)
        assert False
    except LoadError as error:
        assert str(error) == "Load must be >= 0 and <= 100."

    try:
        LoadFilter(servers_).apply(101)
        assert False
    except LoadError as error:
        assert str(error) == "Load must be >= 0 and <= 100."


def test_load_filter_when_load_is_not_an_integer():
    servers_ = get_servers_stub()

    try:
        LoadFilter(servers_).apply("1001")
        assert False
    except LoadError as error:
        assert str(error) == "Wrong type \"<class 'str'>\": 1001"


def test_load_filter_when_servers_is_None():
    try:
        LoadFilter(None).apply(10)
        assert False
    except TypeError as error:
        assert str(error) == "Servers may not be None"


def test_load_filter_when_servers_is_empty_list():
    actual_servers = LoadFilter(list()).apply(10)
    expected_servers = list()

    assert actual_servers == expected_servers


def test_max_load_filter_when_load_is_valid():
    servers_ = get_servers_stub()

    actual_servers = MaxLoadFilter(servers_).apply(10)
    domains = list()
    domains.append("nl80")
    expected_servers = get_expected_servers_by_domain(domains)

    assert actual_servers == expected_servers


def test_min_load_filter_when_load_is_valid():
    servers_ = get_servers_stub()

    actual_servers = MinLoadFilter(servers_).apply(20)
    domains = list()
    domains.append("de111")
    domains.append("de112")
    domains.append("de113")
    domains.append("nl81")
    domains.append("nl82")
    domains.append("us-ca5")
    domains.append("us2853")
    expected_servers = get_expected_servers_by_domain(domains)

    assert actual_servers == expected_servers


def test_filter_servers_when_match_is_max():
    servers_ = get_servers_stub()

    actual_servers = filter_servers(servers_, 10, "max")
    domains = list()
    domains.append("nl80")
    expected_servers = get_expected_servers_by_domain(domains)

    assert actual_servers == expected_servers


def test_filter_servers_when_match_is_default():
    servers_ = get_servers_stub()

    actual_servers = filter_servers(servers_, 10)
    domains = list()
    domains.append("nl80")
    expected_servers = get_expected_servers_by_domain(domains)

    assert actual_servers == expected_servers


def test_filter_servers_when_match_is_min():
    servers_ = get_servers_stub()

    actual_servers = filter_servers(servers_, 20, "min")
    domains = list()
    domains.append("de111")
    domains.append("de112")
    domains.append("de113")
    domains.append("nl81")
    domains.append("nl82")
    domains.append("us-ca5")
    domains.append("us2853")
    expected_servers = get_expected_servers_by_domain(domains)

    assert actual_servers == expected_servers


def test_filter_servers_when_match_is_exact():
    servers_ = get_servers_stub()

    actual_servers = filter_servers(servers_, 20, "exact")
    domains = list()
    domains.append("de112")
    domains.append("de113")
    expected_servers = get_expected_servers_by_domain(domains)

    assert actual_servers == expected_servers


def test_filter_servers_when_match_is_invalid():
    servers_ = get_servers_stub()

    try:
        filter_servers(servers_, 10, "wrong")
        assert False
    except ValueError as error:
        assert str(error) == 'Match must be one of "exact","max" or "min".'
