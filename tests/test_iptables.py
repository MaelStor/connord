#!/usr/bin/env python

# import imp
# from connord import iptables
# mocker.patch(
# 'connord.iptables.user.needs_root', lambda *x, **y: lambda f: f)

# from connord import user
from main_test_module import _get_expected_servers_by_domain


def test_get_table_name_when_config_is_valid():
    from connord import iptables

    config_file = "/etc/connord/01-filter.rules"
    actual_result = iptables.get_table_name(config_file)
    expected_result = "filter"

    assert actual_result == expected_result

    config_file = "01-filter.rules"
    actual_result = iptables.get_table_name(config_file)
    expected_result = "filter"

    assert actual_result == expected_result

    config_file = "filter.rules"
    actual_result = iptables.get_table_name(config_file)
    expected_result = "filter"

    assert actual_result == expected_result

    config_file = "/doesnotexist/filter.rules"
    actual_result = iptables.get_table_name(config_file)
    expected_result = "filter"

    assert actual_result == expected_result

    config_file = "invalid.rules"
    actual_result = iptables.get_table_name(config_file)
    expected_result = "invalid"

    assert actual_result == expected_result

    config_file = "invalid6.rules"
    actual_result = iptables.get_table_name(config_file)
    expected_result = "invalid6"

    assert actual_result == expected_result


def test_get_table_name_when_config_is_invalid_throws(mocker):
    from connord import iptables

    # import sys

    config_file = "/doesnotexist/filter.invalid"

    mocked_regex = mocker.Mock()
    mocked_regex.search.return_value = None
    mocked_re = mocker.patch("connord.iptables.re")
    mocked_re.compile.return_value = mocked_regex

    try:
        iptables.get_table_name(config_file)
        assert False
    except iptables.IptablesError as error:
        assert (
            str(error)
            == "Error: filter.invalid is not a valid filename \
for a .rules file."
        )

    mocked_regex.search.assert_called_once_with("filter.invalid")


def test_init_table_from_file_name_when_user_is_not_root(mocker):
    config_file = "filter.iptables"

    mocked_is_root = mocker.patch("connord.iptables.user.is_root")
    mocked_is_root.return_value = False

    from connord import iptables

    try:
        iptables.init_table_from_file_name(config_file)
        assert False
    except PermissionError as error:
        assert (
            str(error)
            == "Function 'init_table_from_file_name' needs \
root access.".format(
                config_file
            )
        )

    mocked_is_root.assert_called_once()


def test_init_table_from_file_name_when_config_is_valid(mocker):
    config_file = "filter.iptables"
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True
    mocked_table_name = mocker.patch("connord.iptables.get_table_name")
    mocked_table_name.return_value = "filter"

    from connord import iptables

    mocked_table = mocker.patch.object(iptables, "Table")
    mocked_init_table = mocker.patch("connord.iptables.init_table")
    mocked_init_table.return_value = mocked_table

    iptables.init_table_from_file_name(config_file)

    mocked_user.assert_called()
    mocked_table_name.assert_called_once_with(config_file)
    mocked_init_table.assert_called_once_with("filter")


def test_init_table_from_file_name_when_config_is_invalid(mocker):
    config_file = "invalid"

    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True

    from connord import iptables

    mocked_table_str = mocker.patch("connord.iptables.get_table_name")
    mocked_table_str.side_effect = iptables.IptablesError(
        "Error: invalid is not a valid filename for a .rules file."
    )

    try:
        iptables.init_table_from_file_name(config_file)
        assert False
    except iptables.IptablesError as error:
        assert (
            str(error)
            == "Error: invalid is not a valid filename for a \
.rules file."
        )

    mocked_table_str.assert_called_once_with(config_file)
    mocked_user.assert_called_once()


def test_init_table_from_file_name_when_table_is_invalid(mocker):
    config_file = "invalid.rules"
    mocked_table_str = mocker.patch("connord.iptables.get_table_name")
    mocked_table_str.return_value = "invalid"
    mocked_init_table = mocker.patch("connord.iptables.init_table")
    mocked_init_table.side_effect = TypeError("Error: 'invalid' is not a valid table.")
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True

    from connord import iptables

    try:
        iptables.init_table_from_file_name(config_file)
        assert False
    except TypeError as error:
        assert str(error) == "Error: 'invalid' is not a valid table."

    mocked_table_str.assert_called_once_with(config_file)
    mocked_user.assert_called_once()
    mocked_init_table.assert_called_once_with("invalid")


def test_init_table_when_user_is_not_root(mocker):
    table_name = "filter"
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = False

    from connord import iptables

    try:
        iptables.init_table(table_name)
        assert False
    except PermissionError as error:
        assert str(error) == "Function 'init_table' needs root access."

    mocked_user.assert_called_once()


def test_init_table_when_table_is_valid_ipv6(mocker):
    table_name = "filter6"
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True

    from connord import iptables

    table_mock = mocker.Mock()
    mocked_table = mocker.patch.object(iptables, "Table6", table_mock)
    mocker.patch.object(iptables.Table6, "ALL", ["filter"])

    iptables.init_table(table_name)

    mocked_user.assert_called_once()
    mocked_table.assert_called_once_with("filter")


def test_init_table_when_table_is_invalid_ipv6(mocker):
    table_name = "invalid6"
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True

    from connord import iptables

    table_mock = mocker.Mock()
    mocked_table = mocker.patch.object(iptables, "Table6", table_mock)
    mocker.patch.object(iptables.Table6, "ALL", ["filter"])

    try:
        iptables.init_table(table_name)
        assert False
    except TypeError as error:
        assert str(error) == "Error: 'invalid' is not a valid table."

    mocked_user.assert_called_once()
    mocked_table.assert_not_called()


def test_init_table_when_table_is_valid_ipv4(mocker):
    table_name = "filter"
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True

    from connord import iptables

    table_mock = mocker.Mock()
    mocked_table = mocker.patch.object(iptables, "Table", table_mock)
    mocker.patch.object(iptables.Table, "ALL", ["filter"])

    iptables.init_table(table_name)

    mocked_user.assert_called_once()
    mocked_table.assert_called_once_with("filter")


def test_init_table_when_table_is_invalid_ipv4(mocker):
    table_name = "invalid"
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True

    from connord import iptables

    table_mock = mocker.Mock()
    mocked_table = mocker.patch.object(iptables, "Table", table_mock)
    mocker.patch.object(iptables.Table, "ALL", ["filter"])

    try:
        iptables.init_table(table_name)
        assert False
    except TypeError as error:
        assert str(error) == "Error: 'invalid' is not a valid table."

    mocked_user.assert_called_once()
    mocked_table.assert_not_called()


def set_up(mocker):
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True


def test_apply_config_good(mocker):
    config = {
        "FORWARD": {"action": "None", "policy": "DROP", "rules": []},
        "INPUT": {
            "action": "None",
            "policy": "DROP",
            "rules": [
                {"in-interface": "lo", "target": "connord-lo-input"},
                {"in-interface": "tun+", "target": "connord-vpn-input"},
                {"in-interface": "enp0s25", "target": "connord-lan-input"},
            ],
        },
        "OUTPUT": {
            "action": "None",
            "policy": "DROP",
            "rules": [
                {"conntrack": {"ctstate": "RELATED,ESTABLISHED"}, "target": "ACCEPT"},
                {"out-interface": "lo", "target": "connord-lo-output"},
                {"out-interface": "enp0s25", "target": "connord-lan-output"},
                {"out-interface": "tun+", "target": "connord-vpn-output"},
            ],
        },
    }
    config_file = "tests/fixtures/iptables.filter.yml"
    mocked_init_table = mocker.patch("connord.iptables.init_table_from_file_name")
    mocked_table = mocker.Mock()
    mocked_init_table.return_value(mocked_table)
    mocked_iptc = mocker.patch("connord.iptables.iptc")
    mocked_iptc.easy.flush_table.return_value = True
    mocked_iptc.easy.has_chain.return_value = False
    mocked_is_table_v6 = mocker.patch("connord.iptables.is_table_v6")
    mocked_is_table_v6.return_value = False
    mocked_read_config = mocker.patch("connord.iptables.read_config")
    mocked_read_config.return_value = config

    set_up(mocker)
    from connord import iptables

    iptables.apply_config(config_file, None, None)

    mocked_init_table.assert_called_once_with(config_file)
    mocked_iptc.easy.flush_table.assert_called_once()
    mocked_is_table_v6.assert_called_once()
    # mocked_iptc.Chain.assert_called()
    mocked_iptc.easy.has_chain.assert_called()
    mocked_iptc.easy.add_chain.assert_called()
    mocked_iptc.Policy.assert_called()
    mocked_iptc.easy.set_policy.assert_called()
    mocked_iptc.easy.test_rule.assert_called()
    mocked_iptc.easy.add_rule.assert_called()


def test_apply_config_bad(mocker):
    config = {
        "FORWARD": {"action": "None", "policy": "DROP", "rules": []},
        "INPUT": {
            "action": "None",
            "policy": "DROP",
            "rules": [
                {"in-interface": "lo", "target": "connord-lo-input"},
                {"in-interface": "tun+", "target": "connord-vpn-input"},
                {"in-interface": "enp0s25", "target": "connord-lan-input"},
            ],
        },
        "OUTPUT": {
            "action": "None",
            "policy": "DROP",
            "rules": [
                {"conntrack": {"ctstate": "RELATED,ESTABLISHED"}, "target": "ACCEPT"},
                {"out-interface": "lo", "target": "connord-lo-output"},
                {"out-interface": "enp0s25", "target": "connord-lan-output"},
                {"out-interface": "tun+", "target": "connord-vpn-output"},
            ],
        },
    }
    config_file = "tests/fixtures/iptables.filter.yml"
    mocked_init_table = mocker.patch("connord.iptables.init_table_from_file_name")
    mocked_table = mocker.Mock()
    mocked_init_table.return_value(mocked_table)
    mocked_iptc = mocker.patch("connord.iptables.iptc")
    mocked_iptc.easy.flush_table.return_value = True
    mocked_iptc.easy.has_chain.return_value = False
    mocked_is_table_v6 = mocker.patch("connord.iptables.is_table_v6")
    mocked_is_table_v6.return_value = False
    mocked_iptc.easy.test_rule.return_value = False
    mocked_read_config = mocker.patch("connord.iptables.read_config")
    mocked_read_config.return_value = config

    set_up(mocker)
    from connord import iptables

    try:
        iptables.apply_config(config_file, None, "udp")
        assert False
    except iptables.IptablesError as error:
        assert (
            str(error)
            == "Malformed rule: {'in-interface': 'lo', 'target': \
'connord-lo-input'}"
        )

    mocked_init_table.assert_called_once_with(config_file)
    mocked_iptc.easy.flush_table.assert_called_once()
    mocked_is_table_v6.assert_called_once()
    # mocked_iptc.Chain.assert_called()
    mocked_iptc.easy.has_chain.assert_called()
    mocked_iptc.easy.add_chain.assert_called()
    mocked_iptc.Policy.assert_called()
    mocked_iptc.easy.set_policy.assert_called()
    mocked_iptc.easy.test_rule.assert_called()
    mocked_iptc.easy.add_rule.assert_not_called()


def test_is_table_v6(mocker):
    mocked_table = mocker.Mock()

    from connord import iptables

    retval = iptables.is_table_v6(mocked_table)

    assert not retval


def test_apply_config_dir_when_apply_config_bad(mocker):
    _config_files = ["testing", "config"]
    _config_dir = "testdir"

    mocked_find = mocker.patch("connord.iptables.config.list_config_dir")
    mocked_find.return_value = _config_files
    mocked_apply = mocker.patch("connord.iptables.apply_config")
    mocked_apply.return_value = False

    set_up(mocker)
    from connord import iptables

    retval = iptables.apply_config_dir(None, None)

    mocked_find.assert_called_once_with(filetype="rules")
    mocked_apply.assert_called()
    assert not retval


def test_read_config():
    pass
