#!/usr/bin/env python

from connord import features
from main_test_module import _get_servers_stub, _get_expected_servers_by_domain


def test_verify_features_bad():
    # test features is not a list with string
    _features = "some string"
    try:
        features.verify_features(_features)
        assert False
    except features.FeatureError as error:
        assert str(error) == "Wrong server features: some string"

    # test features is not a list with integer
    _features = 123
    try:
        features.verify_features(_features)
        assert False
    except features.FeatureError as error:
        assert str(error) == "Wrong server features: 123"

    # test mix of correct and wrong features
    _features = ["openvpn_udp", "wrong"]
    try:
        features.verify_features(_features)
        assert False
    except features.FeatureError as error:
        assert str(error) == "Wrong server features: ['wrong']"

    # test mix of multiple correct and wrong features
    _features = ["openvpn_udp", "socks", "wrong", "even_worse"]
    try:
        features.verify_features(_features)
        assert False
    except features.FeatureError as error:
        assert str(error) == "Wrong server features: ['wrong', 'even_worse']"

    # test multiple features are all wrong
    _features = ["wrong", "also_wrong", 123]
    try:
        features.verify_features(_features)
        assert False
    except features.FeatureError as error:
        assert str(error) == "Wrong server features: ['wrong', 'also_wrong', 123]"


def test_filter_servers_good():
    servers_stub = _get_servers_stub()

    # test default features argument is None
    try:
        actual_servers = features.filter_servers(servers_stub)
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "us2853"]
        )
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test default features argument is empyt list
    try:
        actual_servers = features.filter_servers(servers_stub)
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "us2853"]
        )
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test multiple features are good
    try:
        actual_servers = features.filter_servers(
            servers_stub, ["openvpn_udp", "openvpn_tcp"]
        )
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "us2853"]
        )
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False


def test_filter_servers_with_every_feature():
    servers_stub = _get_servers_stub()

    # test with ikev2
    try:
        actual_servers = features.filter_servers(servers_stub, ["ikev2"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_udp
    try:
        actual_servers = features.filter_servers(servers_stub, ["openvpn_udp"])
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "us2853"]
        )
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_tcp
    try:
        actual_servers = features.filter_servers(servers_stub, ["openvpn_tcp"])
        expected_servers = _get_expected_servers_by_domain(
            ["de111", "de112", "de113", "us-ca5", "us2853"]
        )
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with socks
    try:
        actual_servers = features.filter_servers(servers_stub, ["socks"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with proxy
    try:
        actual_servers = features.filter_servers(servers_stub, ["proxy"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with pptp
    try:
        actual_servers = features.filter_servers(servers_stub, ["pptp"])
        assert actual_servers == list()
    except features.FeatureError:
        assert False

    # test with l2tp
    try:
        actual_servers = features.filter_servers(servers_stub, ["l2tp"])
        assert actual_servers == list()
    except features.FeatureError:
        assert False

    # test with openvpn_xor_udp
    try:
        actual_servers = features.filter_servers(servers_stub, ["openvpn_xor_udp"])
        expected_servers = _get_expected_servers_by_domain(["nl80", "nl81", "nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_xor_tcp
    try:
        actual_servers = features.filter_servers(servers_stub, ["openvpn_xor_tcp"])
        expected_servers = _get_expected_servers_by_domain(["nl80", "nl81", "nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with proxy_cybersec
    try:
        actual_servers = features.filter_servers(servers_stub, ["proxy_cybersec"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112", "de113"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with proxy_ssl
    try:
        actual_servers = features.filter_servers(servers_stub, ["proxy_ssl"])
        expected_servers = _get_expected_servers_by_domain(["de112", "de113"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with proxy_ssl_cybersec
    try:
        actual_servers = features.filter_servers(servers_stub, ["proxy_ssl_cybersec"])
        expected_servers = _get_expected_servers_by_domain(["de111", "de112"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with ikev2_v6
    try:
        actual_servers = features.filter_servers(servers_stub, ["ikev2_v6"])
        expected_servers = _get_expected_servers_by_domain(["nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_udp_v6
    try:
        actual_servers = features.filter_servers(servers_stub, ["openvpn_udp_v6"])
        expected_servers = _get_expected_servers_by_domain(["nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_tcp_v6
    try:
        actual_servers = features.filter_servers(servers_stub, ["openvpn_tcp_v6"])
        expected_servers = _get_expected_servers_by_domain(["nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with wireguard_udp
    try:
        actual_servers = features.filter_servers(servers_stub, ["wireguard_udp"])
        expected_servers = _get_expected_servers_by_domain(["nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_udp_tls_crypt
    try:
        actual_servers = features.filter_servers(
            servers_stub, ["openvpn_udp_tls_crypt"]
        )
        expected_servers = _get_expected_servers_by_domain(["nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False

    # test with openvpn_tcp_tls_crypt
    try:
        actual_servers = features.filter_servers(
            servers_stub, ["openvpn_tcp_tls_crypt"]
        )
        expected_servers = _get_expected_servers_by_domain(["nl82"])
        assert actual_servers == expected_servers
    except features.FeatureError:
        assert False


def test_to_string():
    with open(
        "tests/fixtures/features_to_string_stub.txt", "r"
    ) as features_to_string_stub:
        expected_result = features_to_string_stub.read()

    actual_result = features.to_string()

    assert actual_result == expected_result


def test_print_features():
    # Just expect no exception
    try:
        features.print_features()
        assert True
    except Exception:
        assert False
