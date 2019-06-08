#!/usr/bin/env python

from connord import listings
from main_test_module import _get_stub, _get_servers_stub


def test_list_iptables(mocker):
    mocked_iptables = mocker.patch("connord.listings.iptables")
    mocked_iptables.to_string.return_value = "testing"

    retval = listings.list_iptables(["filter"], "4")

    mocked_iptables.print_iptables.assert_called_once_with(["filter"], "4")
    assert retval


def test_listings_when_countries_has_a_none_value(capsys):
    expected_result = _get_stub("countries_pretty_formatted_fixture.txt")

    _countries = [None]
    retval = listings.main(_countries, None, None, None, None, None, None, None)

    captured = capsys.readouterr()
    assert captured.out == expected_result
    assert retval
    assert captured.err == str()


def test_listings_when_types_has_a_none_value(capsys):
    expected_result = _get_stub("types_pretty_formatted_fixture.txt")

    _types = [None]
    retval = listings.main(None, None, _types, None, None, None, None, None)

    captured = capsys.readouterr()
    assert captured.out == expected_result
    assert retval
    assert captured.err == str()


def test_listings_when_features_has_a_none_value(capsys):
    expected_result = _get_stub("features_pretty_formatted_fixture.txt")

    _features = [None]
    retval = listings.main(None, None, None, _features, None, None, None, None)

    captured = capsys.readouterr()
    assert captured.out == expected_result
    assert retval
    assert captured.err == str()


def test_listings_when_area_has_a_none_value():
    try:
        _area = [None]
        listings.main(None, _area, None, None, None, None, None, None)
        assert False
    except NotImplementedError as error:
        assert str(error) == "Area filter is not implemented yet."


def test_listings_when_every_option_is_given_and_countries_is_none(capsys, mocker):
    _servers = _get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = _servers
    mocked_servers.to_string.return_value = "testing"

    retval = listings.main(None, None, None, None, False, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert retval
    assert captured.out == ""
    assert captured.err == ""


def test_listings_when_every_option_is_given_and_countries_is_empty(capsys, mocker):
    _servers = _get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = _servers

    retval = listings.main(list(), None, None, None, True, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert retval
    assert captured.out == ""
    assert captured.err == ""


def test_listings_when_every_option_is_given_with_types_features(capsys, mocker):
    _servers = _get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = _servers

    _types = ["standard"]
    _features = ["openvpn_udp"]
    retval = listings.main(list(), None, _types, _features, True, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert retval
    assert captured.out == ""
    assert captured.err == ""
