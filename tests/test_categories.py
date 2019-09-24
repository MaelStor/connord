#!/usr/bin/env python
"""Test categories module"""

from connord import categories
from main_test_module import get_expected_servers_by_domain, get_servers_stub, get_stub


def test_verify_categories_good():
    categories_ = ["standard"]
    assert categories.verify_categories(categories_)


def test_verify_categories_order_does_not_matter():
    categories_ = ["standard", "double", "p2p", "obfuscated", "dedicated"]
    assert categories.verify_categories(categories_)


def test_verify_categories_bad():
    # test categories is not a list with string
    categories_ = "some string"
    try:
        categories.verify_categories(categories_)
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong server categories: some string"

    # test categories is not a list with integer
    categories_ = 123
    try:
        categories.verify_categories(categories_)
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong server categories: 123"

    # test mix of correct and wrong categories
    categories_ = ["standard", "wrong"]
    try:
        categories.verify_categories(categories_)
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong server categories: ['wrong']"

    # test mix of multiple correct and wrong categories
    categories_ = ["standard", "dedicated", "wrong", "even_worse"]
    try:
        categories.verify_categories(categories_)
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong server categories: ['wrong', 'even_worse']"

    # test multiple categories are all wrong
    categories_ = ["wrong", "also_wrong", 123]
    try:
        categories.verify_categories(categories_)
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong server categories: ['wrong', 'also_wrong', 123]"


def test_filter_servers_good():
    servers_stub = get_servers_stub()
    # test default categories with no argument
    try:
        actual_servers = categories.filter_servers(servers_stub)
        expected_servers = get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test default type argument with empty list
    try:
        actual_servers = categories.filter_servers(servers_stub, list())
        expected_servers = get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test multiple categories
    try:
        actual_servers = categories.filter_servers(servers_stub, ["standard", "p2p"])
        expected_servers = get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test all categories at once should return empty list
    try:
        actual_servers = categories.filter_servers(
            servers_stub, ["double", "dedicated", "standard", "p2p", "obfuscated"]
        )
        assert actual_servers == list()
    except categories.CategoriesError:
        assert False


def test_filter_servers_with_every_type():
    servers_stub = get_servers_stub()

    # test with double
    try:
        actual_servers = categories.filter_servers(servers_stub, ["double"])
        expected_servers = get_expected_servers_by_domain(["us-ca5"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test with dedicated
    try:
        actual_servers = categories.filter_servers(servers_stub, ["dedicated"])
        expected_servers = get_expected_servers_by_domain(["us2853"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test with standard
    try:
        actual_servers = categories.filter_servers(servers_stub, ["standard"])
        expected_servers = get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test with p2p
    try:
        actual_servers = categories.filter_servers(servers_stub, ["p2p"])
        expected_servers = get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False

    # test with obfuscated
    try:
        actual_servers = categories.filter_servers(servers_stub, ["obfuscated"])
        expected_servers = get_expected_servers_by_domain(["nl80", "nl81", "nl82"])
        assert actual_servers == expected_servers
    except categories.CategoriesError:
        assert False


def test_map_categories_good():
    # test mapping with one correct type
    categories_ = ["standard"]
    expected_mapped_categories = ["Standard VPN servers"]
    actual_mapped_categories = categories.map_categories(categories_)
    assert actual_mapped_categories == expected_mapped_categories

    # test mapping with multiple correct categories
    categories_ = ["standard", "dedicated"]
    expected_mapped_categories = ["Standard VPN servers", "Dedicated IP"]
    actual_mapped_categories = categories.map_categories(categories_)
    assert actual_mapped_categories == expected_mapped_categories


def test_map_categories_reverse_good():
    # test mapping with one correct type
    categories_ = ["Standard VPN servers"]
    expected_mapped_categories = ["standard"]
    actual_mapped_categories = categories.map_categories_reverse(categories_)
    assert actual_mapped_categories == expected_mapped_categories

    # test mapping with multiple correct categories
    categories_ = ["Standard VPN servers", "Dedicated IP"]
    expected_mapped_categories = ["standard", "dedicated"]
    actual_mapped_categories = categories.map_categories_reverse(categories_)
    assert actual_mapped_categories == expected_mapped_categories


def test_map_categories_reverse_bad():
    # test with one wrong type
    try:
        categories.map_categories_reverse(["wrong"])
        assert False
    except categories.CategoriesError:
        assert True

    # test with multiple wrong categories
    try:
        categories.map_categories_reverse(["wrong", "alsowrong"])
        assert False
    except categories.CategoriesError:
        assert True

    # test error message
    try:
        categories.map_categories_reverse(["wrong"])
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong category descriptions: ['wrong']"

    # test error message with multiple wrong categories
    try:
        categories.map_categories_reverse(["wrong", "alsowrong"])
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong category descriptions: ['wrong', 'alsowrong']"

    # test when description type is string should raise CategoriesError
    try:
        categories.map_categories_reverse("some string")
        assert False
    except categories.CategoriesError as error:
        assert str(error) == "Wrong type: <class 'str'>"


def test_to_string():
    expected_result = get_stub("categories_pretty_formatted_fixture.txt").rstrip()
    actual_result = categories.to_string()

    assert actual_result == expected_result


def test_print_categories():
    # Just expect no exception
    try:
        categories.print_categories()
        assert True
    except Exception:
        assert False
