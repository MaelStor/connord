#!/usr/bin/env python

from connord import countries
from main_test_module import _get_servers_stub, _get_expected_servers_by_domain


def test_verify_coutries_bad():
    # test param with string should throw CountryError
    country = "some string"
    try:
        countries.verify_countries(country)
        assert False
    except countries.CountryError as error:
        assert str(error) == "Wrong countries: some string"

    # test param with integer should throw CountryError
    country = 123
    try:
        countries.verify_countries(country)
        assert False
    except countries.CountryError as error:
        assert str(error) == "Wrong countries: 123"

    # test param with mix of correct and wrong countries
    _countries = ["gb", "de", "kk", "zz"]
    try:
        countries.verify_countries(_countries)
        assert False
    except countries.CountryError as error:
        assert str(error) == "Wrong countries: ['kk', 'zz']"

    # test param with all countries are wrong should throw
    _countries = ["uk", "kk", "zz"]
    try:
        countries.verify_countries(_countries)
        assert False
    except countries.CountryError as error:
        assert str(error) == "Wrong countries: ['uk', 'kk', 'zz']"


def test_verify_coutries_good():
    # test param with one item
    _countries = ["gb"]
    try:
        rc = countries.verify_countries(_countries)
        assert rc
    except countries.CountryError:
        assert False

    # test param with multiple items
    _countries = ["gb", "de", "us"]
    try:
        rc = countries.verify_countries(_countries)
        assert rc
    except countries.CountryError:
        assert False

    # test param with all possible countries
    _countries = [
        "ae",
        "al",
        "ar",
        "at",
        "au",
        "ba",
        "be",
        "bg",
        "br",
        "ca",
        "ch",
        "cl",
        "cr",
        "cy",
        "cz",
        "de",
        "dk",
        "ee",
        "eg",
        "es",
        "fi",
        "fr",
        "gb",
        "ge",
        "gr",
        "hk",
        "hr",
        "hu",
        "id",
        "ie",
        "il",
        "in",
        "is",
        "it",
        "jp",
        "kr",
        "lu",
        "lv",
        "md",
        "mk",
        "mx",
        "my",
        "nl",
        "no",
        "nz",
        "pl",
        "pt",
        "ro",
        "rs",
        "se",
        "sg",
        "si",
        "sk",
        "th",
        "tr",
        "tw",
        "ua",
        "us",
        "vn",
        "za",
    ]
    try:
        rc = countries.verify_countries(_countries)
        assert rc
    except countries.CountryError:
        assert False


def test_filter_servers_good():
    servers_stub = _get_servers_stub()

    # test param when param is not given
    try:
        actual_servers = countries.filter_servers(servers_stub)
        expected_servers = servers_stub
        assert actual_servers == expected_servers
    except countries.CountryError:
        assert False

    # test param when param is an empty list
    try:
        actual_servers = countries.filter_servers(servers_stub)
        expected_servers = servers_stub
        assert actual_servers == expected_servers
    except countries.CountryError:
        assert False

    # test param with multiple valid countries
    try:
        actual_servers = countries.filter_servers(servers_stub, ["de", "nl"])
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "nl80", "nl81", "nl82"]
        )
        assert actual_servers == expected_servers
    except countries.CountryError:
        assert False

    # test with uppercase country code
    try:
        actual_servers = countries.filter_servers(servers_stub, ["DE"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except countries.CountryError:
        assert False

    # test with mixedcase country code
    try:
        actual_servers = countries.filter_servers(servers_stub, ["De"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except countries.CountryError:
        assert False

    # test with multiple mixedcase country codes
    try:
        actual_servers = countries.filter_servers(servers_stub, ["De", "nL"])
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "nl80", "nl81", "nl82"]
        )
        assert actual_servers == expected_servers
    except countries.CountryError:
        assert False

    # test param: server is empty
    try:
        actual_servers = countries.filter_servers(list(), ["de"])
        assert actual_servers == list()
    except BaseException:
        assert False


def test_filter_servers_bad():
    # test param server is None
    try:
        countries.filter_servers(None, ["de"])
        assert False
    except TypeError as error:
        assert str(error) == "Servers may not be None"


def test_to_string():
    with open("tests/fixtures/countries_to_string_stub.txt") as file_handle:
        expected_result = file_handle.read()

    actual_result = countries.to_string()
    assert actual_result == expected_result


def test_print_countries():
    # test only if no exception occurs
    try:
        countries.print_countries()
        assert True
    except Exception:
        assert False
