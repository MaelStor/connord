#!/usr/bin/env python

from connord import listings
from tests.main_test_module import get_stub, get_servers_stub


def test_list_iptables(mocker):
    mocked_iptables = mocker.patch("connord.listings.iptables")
    mocked_iptables.to_string.return_value = "testing"

    retval = listings.list_iptables(["filter"], "4")

    mocked_iptables.print_iptables.assert_called_once_with(["filter"], "4")
    assert retval


def test_listings_when_every_option_is_given_and_countries_is_none(capsys, mocker):
    servers_ = get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = servers_
    mocked_servers.to_string.return_value = "testing"

    listings.list_servers(None, None, None, None, False, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert captured.out == ""
    assert captured.err == ""


def test_listings_when_every_option_is_given_and_countries_is_empty(capsys, mocker):
    servers_ = get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = servers_

    listings.list_servers(list(), None, None, None, True, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert captured.out == ""
    assert captured.err == ""


def test_listings_when_every_option_is_given_with_categories_features(capsys, mocker):
    servers_ = get_servers_stub()

    mocked_servers = mocker.patch("connord.listings.servers")
    mocked_servers.get_servers.return_value = servers_

    categories_ = ["standard"]
    features_ = ["openvpn_udp"]
    listings.list_servers(list(), None, categories_, features_, True, 10, "max", 10)
    captured = capsys.readouterr()

    mocked_servers.get_servers.assert_called_once()
    mocked_servers.to_string.assert_called_once()
    assert captured.out == ""
    assert captured.err == ""
