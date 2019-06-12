#!/usr/bin/env python

from connord import listings
from main_test_module import get_stub, get_servers_stub


def test_list_iptables(mocker):
    mocked_iptables = mocker.patch("connord.listings.iptables")
    mocked_iptables.to_string.return_value = "testing"

    retval = listings.list_iptables(["filter"], "4")

    mocked_iptables.print_iptables.assert_called_once_with(["filter"], "4")
    assert retval


def test_listings_when_countries_has_a_none_value(capsys):
    expected_result = get_stub("countries_pretty_formatted_fixture.txt")

    countries_ = [None]
    retval = listings.main(countries_, None, None, None, None, None, None, None)

    captured = capsys.readouterr()
    assert captured.out == expected_result
    assert retval
    assert captured.err == str()


def test_listings_when_types_has_a_none_value(capsys):
    expected_result = get_stub("types_pretty_formatted_fixture.txt")

    types_ = [None]
    retval = listings.main(None, None, types_, None, None, None, None, None)

    captured = capsys.readouterr()
    assert captured.out == expected_result
    assert retval
    assert captured.err == str()


def test_listings_when_features_has_a_none_value(capsys):
    expected_result = get_stub("features_pretty_formatted_fixture.txt")

    features_ = [None]
    retval = listings.main(None, None, None, features_, None, None, None, None)

    captured = capsys.readouterr()
    assert captured.out == expected_result
    assert retval
    assert captured.err == str()


def test_listings_when_area_has_a_none_value(capsys):
    header_fixture = """================================================================================
Mini ID :    Latitude        Longitude     City                                    
Address
================================================================================
"""

    area_ = [None]
    listings.main(None, area_, None, None, None, None, None, None)

    captured = capsys.readouterr()
    assert str(captured.out).startswith(header_fixture)


def test_listings_when_every_option_is_given_and_countries_is_none(capsys, mocker):
    servers_ = get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = servers_
    mocked_servers.to_string.return_value = "testing"

    retval = listings.main(None, None, None, None, False, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert retval
    assert captured.out == ""
    assert captured.err == ""


def test_listings_when_every_option_is_given_and_countries_is_empty(capsys, mocker):
    servers_ = get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = servers_

    retval = listings.main(list(), None, None, None, True, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert retval
    assert captured.out == ""
    assert captured.err == ""


def test_listings_when_every_option_is_given_with_types_features(capsys, mocker):
    servers_ = get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = servers_

    types_ = ["standard"]
    features_ = ["openvpn_udp"]
    retval = listings.main(list(), None, types_, features_, True, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert retval
    assert captured.out == ""
    assert captured.err == ""
