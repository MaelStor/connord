#!/usr/bin/env python
"""Test types module"""

from connord import types
from main_test_module import _get_expected_servers_by_domain, _get_servers_stub


def test_verify_types_good():
    _types = ["standard"]
    assert types.verify_types(_types)


def test_verify_types_order_does_not_matter():
    _types = ["standard", "double", "p2p", "obfuscated", "dedicated"]
    assert types.verify_types(_types)


def test_verify_types_bad():
    # test types is not a list with string
    _types = "some string"
    try:
        types.verify_types(_types)
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: some string"

    # test types is not a list with integer
    _types = 123
    try:
        types.verify_types(_types)
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: 123"

    # test mix of correct and wrong types
    _types = ["standard", "wrong"]
    try:
        types.verify_types(_types)
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: ['wrong']"

    # test mix of multiple correct and wrong types
    _types = ["standard", "dedicated", "wrong", "even_worse"]
    try:
        types.verify_types(_types)
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: ['wrong', 'even_worse']"

    # test multiple types are all wrong
    _types = ["wrong", "also_wrong", 123]
    try:
        types.verify_types(_types)
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: ['wrong', 'also_wrong', 123]"


def test_filter_servers_good():
    servers_stub = _get_servers_stub()
    # test default types with no argument
    try:
        actual_servers = types.filter_servers(servers_stub)
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test default type argument with empty list
    try:
        actual_servers = types.filter_servers(servers_stub, list())
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test multiple types
    try:
        actual_servers = types.filter_servers(servers_stub, ["standard", "p2p"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test all types at once should return empty list
    try:
        actual_servers = types.filter_servers(
            servers_stub, ["double", "dedicated", "standard", "p2p", "obfuscated"]
        )
        assert actual_servers == list()
    except types.ServerTypeError:
        assert False


def test_filter_servers_with_every_type():
    servers_stub = _get_servers_stub()

    # test with double
    try:
        actual_servers = types.filter_servers(servers_stub, ["double"])
        expected_servers = _get_expected_servers_by_domain(["us-ca5"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test with dedicated
    try:
        actual_servers = types.filter_servers(servers_stub, ["dedicated"])
        expected_servers = _get_expected_servers_by_domain(["us2853"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test with standard
    try:
        actual_servers = types.filter_servers(servers_stub, ["standard"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test with p2p
    try:
        actual_servers = types.filter_servers(servers_stub, ["p2p"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False

    # test with obfuscated
    try:
        actual_servers = types.filter_servers(servers_stub, ["obfuscated"])
        expected_servers = _get_expected_servers_by_domain(["nl80", "nl81", "nl82"])
        assert actual_servers == expected_servers
    except types.ServerTypeError:
        assert False


def test_filter_servers_bad():
    servers_stub = _get_servers_stub()

    # test error message with multiple wrong types
    try:
        types.filter_servers(servers_stub, ["wrong", "alsowrong"])
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: ['wrong', 'alsowrong']"


def test_map_types_good():
    # test mapping with one correct type
    _types = ["standard"]
    expected_mapped_types = ["Standard VPN servers"]
    actual_mapped_types = types.map_types(_types)
    assert actual_mapped_types == expected_mapped_types

    # test mapping with multiple correct types
    _types = ["standard", "dedicated"]
    expected_mapped_types = ["Standard VPN servers", "Dedicated IP"]
    actual_mapped_types = types.map_types(_types)
    assert actual_mapped_types == expected_mapped_types


def test_map_types_bad():
    # test with one wrong type
    try:
        types.map_types(["wrong"])
        assert False
    except types.ServerTypeError:
        assert True

    # test with multiple wrong types
    try:
        types.map_types(["wrong", "alsowrong"])
        assert False
    except types.ServerTypeError:
        assert True

    # test error message
    try:
        types.map_types(["wrong"])
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: ['wrong']"

    # test error message with multiple wrong types
    try:
        types.map_types(["wrong", "alsowrong"])
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong server types: ['wrong', 'alsowrong']"


def test_map_types_reverse_good():
    # test mapping with one correct type
    _types = ["Standard VPN servers"]
    expected_mapped_types = ["standard"]
    actual_mapped_types = types.map_types_reverse(_types)
    assert actual_mapped_types == expected_mapped_types

    # test mapping with multiple correct types
    _types = ["Standard VPN servers", "Dedicated IP"]
    expected_mapped_types = ["standard", "dedicated"]
    actual_mapped_types = types.map_types_reverse(_types)
    assert actual_mapped_types == expected_mapped_types


def test_map_types_reverse_bad():
    # test with one wrong type
    try:
        types.map_types_reverse(["wrong"])
        assert False
    except types.ServerTypeError:
        assert True

    # test with multiple wrong types
    try:
        types.map_types_reverse(["wrong", "alsowrong"])
        assert False
    except types.ServerTypeError:
        assert True

    # test error message
    try:
        types.map_types_reverse(["wrong"])
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong type descriptions: ['wrong']"

    # test error message with multiple wrong types
    try:
        types.map_types_reverse(["wrong", "alsowrong"])
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong type descriptions: ['wrong', 'alsowrong']"

    # test when description type is string should throw ServerTypeError
    try:
        types.map_types_reverse("some string")
        assert False
    except types.ServerTypeError as error:
        assert str(error) == "Wrong type: <class 'str'>"


def test_to_string():
    with open("tests/fixtures/types_to_string_stub.txt", "r") as types_to_string_stub:
        expected_result = types_to_string_stub.read()

    actual_result = types.to_string()
    assert actual_result == expected_result


def test_print_types():
    # Just expect no exception
    try:
        types.print_types()
        assert True
    except Exception:
        assert False
