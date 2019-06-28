#!/usr/bin/env python

# pylint: disable=import-error, redefined-outer-name, too-many-locals

import time
import pytest
from connord import connect
from connord.resources import ResourceNotFoundError
from main_test_module import (
    get_servers_stub,
    get_json,
    MockBase,
    get_expected_servers_by_domain,
)


@pytest.fixture
def ping_output_good():
    return b"""PING archlinux.org (192.168.8.1) 56(84) bytes of data.

--- archlinux.org ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 9ms
rtt min/avg/max/mdev = 0.895/0.980/1.040/0.067 ms
"""


@pytest.fixture
def ping_output_bad():
    return b"""PING archlinux.org (192.168.8.1) 56(84) bytes of data.

--- archlinux.org ping statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 9ms
"""


@pytest.fixture
def servers_fix():
    return get_servers_stub()


@pytest.fixture
def servers_12():
    return get_json("servers_fix_12.json")


@pytest.fixture
def pinged_servers():
    servers_ = get_json("servers_fix_12_sorted_by_load_cut_to_10.json")
    for i, server in enumerate(servers_):
        server["ping"] = i
    return servers_


@pytest.fixture
def servers_sorted_by_load():
    return get_json("servers_fix_12_sorted_by_load_cut_to_10.json")


@pytest.fixture
def openvpn_command_no_options():
    server = get_expected_servers_by_domain(["de111"])[0]
    openvpn_command = connect.OpenvpnCommand(server, "", False, "udp")
    return openvpn_command


def test_ping(mocker, ping_output_good):
    test_server = {}
    test_server["ip_address"] = "100.100.100.100"
    test_server["domain"] = "us1000"

    mocked_popen = mocker.patch("connord.connect.subprocess.Popen")
    process_mock = mocker.MagicMock()
    attrs = {"communicate.return_value": (ping_output_good, b"error")}
    process_mock.configure_mock(**attrs)
    mocked_popen.return_value.__enter__.return_value = process_mock

    server = connect.ping(test_server)

    mocked_popen.assert_called()
    assert server["ping"] == 0.980


def test_ping_bad(mocker, ping_output_bad):
    test_server = {}
    test_server["ip_address"] = "100.100.100.100"
    test_server["domain"] = "us1000"

    mocked_popen = mocker.patch("connord.connect.subprocess.Popen")
    process_mock = mocker.MagicMock()
    attrs = {"communicate.return_value": (ping_output_bad, b"error")}
    process_mock.configure_mock(**attrs)
    mocked_popen.return_value.__enter__.return_value = process_mock

    server = connect.ping(test_server)

    mocked_popen.assert_called()
    import math

    assert server["ping"] == math.inf


def test_ping_servers_parallelness(mocker):
    test_server = {}
    test_server["ip_address"] = "100.100.100.100"
    test_server["domain"] = "us1000"

    def ping_fix(ip):
        time.sleep(0.2)
        return test_server

    mocker.patch("connord.connect.ping", ping_fix)
    servers_ = get_servers_stub()
    actual_servers = connect.ping_servers_parallel(servers_)
    expected_servers = []
    for i in range(len(servers_)):
        expected_servers.append(test_server)

    assert actual_servers == expected_servers


def test_filter_servers(mocker, servers_fix):
    mocked_load = mocker.patch("connord.connect.load")
    mocked_load.filter_servers.return_value = servers_fix
    mocked_servers = mocker.patch("connord.connect.servers")
    mocked_servers.filter_netflix_servers.return_value = servers_fix
    mocked_countries = mocker.patch("connord.connect.countries")
    mocked_countries.filter_countries.return_value = servers_fix
    mocked_areas = mocker.patch("connord.connect.areas")
    mocked_areas.filter_servers.return_value = servers_fix
    mocked_types = mocker.patch("connord.connect.types")
    mocked_types.filter_servers.return_value = servers_fix
    mocked_types.has_type.return_value = False
    mocked_features = mocker.patch("connord.connect.features")
    mocked_features.filter_servers.return_value = servers_fix

    # run
    actual_servers = connect.filter_servers(
        servers_fix, True, ["de"], ["fr"], ["some"], ["test"], 10, "max"
    )

    assert actual_servers == servers_fix


def test_filter_best_servers(
    mocker, servers_sorted_by_load, servers_12, pinged_servers
):
    mocked_ping = mocker.patch("connord.connect.ping_servers_parallel")
    mocked_ping.return_value = pinged_servers

    # run
    actual_servers = connect.filter_best_servers(servers_12)

    # assert
    mocked_ping.assert_called_once_with(servers_sorted_by_load)
    assert actual_servers == pinged_servers


def test_connect_to_specific_server(mocker, servers_12):
    mockbase = MockBase("connect")
    mockbase.setup(connect)

    server = servers_12[0]
    mocked_servers = mocker.patch("connord.connect.servers")
    mocked_servers.get_server_by_domain.return_value = server
    mocked_run = mocker.patch("connord.connect.run_openvpn", return_value=True)

    # run
    retval = connect.connect_to_specific_server([server], "", False, "udp")

    # assert
    mocked_servers.get_server_by_domain.assert_called_once_with(server)
    mocked_run.assert_called_once_with(server, "", False, "udp")
    assert retval


def test_connect_when_bet_not_in_domain(mocker):
    # setup
    mockbase = MockBase("connect")
    mockbase.setup(connect)

    mocked_con_spec = mocker.patch(
        "connord.connect.connect_to_specific_server", return_value=True
    )

    domain = ["us1000"]
    countries_ = None
    areas_ = None
    features_ = None
    types_ = None
    netflix = False
    load_ = 10
    match = "max"
    daemon = True
    openvpn = ""
    protocol = "udp"
    # run
    retval = connect.connect(
        domain,
        countries_,
        areas_,
        features_,
        types_,
        netflix,
        load_,
        match,
        daemon,
        openvpn,
        protocol,
    )

    # assert
    mocked_con_spec.assert_called_once_with(domain, openvpn, daemon, protocol)
    assert retval


def test_connect_when_domain_is_best(mocker, pinged_servers, servers_fix):
    # setup
    mockbase = MockBase("connect")
    mockbase.setup(connect)

    mocked_con_spec = mocker.patch(
        "connord.connect.connect_to_specific_server", return_value=True
    )
    mocked_servers = mocker.patch(
        "connord.connect.servers.get_servers", return_value=servers_fix
    )
    mocked_filter = mocker.patch(
        "connord.connect.filter_servers", return_value=servers_fix
    )
    mocked_best = mocker.patch(
        "connord.connect.filter_best_servers", return_value=pinged_servers
    )
    mocked_run = mocker.patch("connord.connect.run_openvpn", return_value=True)

    domain = ["best"]
    countries_ = None
    areas_ = None
    features_ = None
    types_ = None
    netflix = False
    load_ = 10
    match = "max"
    daemon = True
    openvpn = ""
    protocol = "udp"
    # run
    retval = connect.connect(
        domain,
        countries_,
        areas_,
        features_,
        types_,
        netflix,
        load_,
        match,
        daemon,
        openvpn,
        protocol,
    )

    # assert
    mocked_con_spec.assert_not_called()
    mocked_servers.assert_called_once()
    mocked_filter.assert_called_once_with(
        servers_fix, netflix, countries_, areas_, features_, types_, load_, match
    )
    mocked_best.assert_called_once_with(servers_fix)
    mocked_run.assert_called_once_with(pinged_servers[0], openvpn, daemon, protocol)
    assert retval


def test_connect_when_domain_is_best_max_retries_reached(
    mocker, pinged_servers, servers_fix
):
    # setup
    mockbase = MockBase("connect")
    mockbase.setup(connect)

    mocked_con_spec = mocker.patch(
        "connord.connect.connect_to_specific_server", return_value=True
    )
    mocked_servers = mocker.patch(
        "connord.connect.servers.get_servers", return_value=servers_fix
    )
    mocked_filter = mocker.patch(
        "connord.connect.filter_servers", return_value=servers_fix
    )
    mocked_best = mocker.patch(
        "connord.connect.filter_best_servers", return_value=pinged_servers
    )
    mocked_run = mocker.patch("connord.connect.run_openvpn")
    mocked_run.side_effect = [False, False, False]

    domain = ["best"]
    countries_ = None
    areas_ = None
    features_ = None
    types_ = None
    netflix = False
    load_ = 10
    match = "max"
    daemon = True
    openvpn = ""
    protocol = "udp"
    # run
    try:
        connect.connect(
            domain,
            countries_,
            areas_,
            features_,
            types_,
            netflix,
            load_,
            match,
            daemon,
            openvpn,
            protocol,
        )
        assert False
    except connect.ConnectError as error:
        assert str(error) == "Maximum retries reached."

    # assert
    mocked_con_spec.assert_not_called()
    mocked_servers.assert_called_once()
    mocked_filter.assert_called_once_with(
        servers_fix, netflix, countries_, areas_, features_, types_, load_, match
    )
    mocked_best.assert_called_once_with(servers_fix)
    mocked_run.assert_called()


def test_connect_when_domain_is_best_no_server_left_with_valid_ping(
    mocker, pinged_servers, servers_fix
):
    # setup
    mockbase = MockBase("connect")
    mockbase.setup(connect)

    mocked_con_spec = mocker.patch(
        "connord.connect.connect_to_specific_server", return_value=True
    )
    mocked_servers = mocker.patch(
        "connord.connect.servers.get_servers", return_value=servers_fix
    )
    mocked_filter = mocker.patch(
        "connord.connect.filter_servers", return_value=servers_fix
    )
    import math

    for server in pinged_servers:
        server["ping"] = math.inf

    mocked_best = mocker.patch(
        "connord.connect.filter_best_servers", return_value=pinged_servers
    )
    mocked_run = mocker.patch("connord.connect.run_openvpn")

    domain = ["best"]
    countries_ = None
    areas_ = None
    features_ = None
    types_ = None
    netflix = False
    load_ = 10
    match = "max"
    daemon = True
    openvpn = ""
    protocol = "udp"
    # run
    try:
        connect.connect(
            domain,
            countries_,
            areas_,
            features_,
            types_,
            netflix,
            load_,
            match,
            daemon,
            openvpn,
            protocol,
        )
        assert False
    except connect.ConnectError as error:
        assert str(error) == "No server left with a valid ping."

    # assert
    mocked_con_spec.assert_not_called()
    mocked_servers.assert_called_once()
    mocked_filter.assert_called_once_with(
        servers_fix, netflix, countries_, areas_, features_, types_, load_, match
    )
    mocked_best.assert_called_once_with(servers_fix)
    mocked_run.assert_not_called()


def test_connect_when_domain_is_best_two_servers_run_openvpn_fails(
    mocker, pinged_servers, servers_fix
):
    # setup
    mockbase = MockBase("connect")
    mockbase.setup(connect)

    mocked_con_spec = mocker.patch(
        "connord.connect.connect_to_specific_server", return_value=True
    )
    mocked_servers = mocker.patch(
        "connord.connect.servers.get_servers", return_value=servers_fix
    )
    mocked_filter = mocker.patch(
        "connord.connect.filter_servers", return_value=servers_fix
    )

    two_servers = pinged_servers[:2]
    counter = 1
    for server in two_servers:
        server["ping"] = counter
        counter += 1

    mocked_best = mocker.patch(
        "connord.connect.filter_best_servers", return_value=two_servers
    )
    mocked_run = mocker.patch("connord.connect.run_openvpn", return_value=False)

    domain = ["best"]
    countries_ = None
    areas_ = None
    features_ = None
    types_ = None
    netflix = False
    load_ = 10
    match = "max"
    daemon = True
    openvpn = ""
    protocol = "udp"
    # run
    try:
        connect.connect(
            domain,
            countries_,
            areas_,
            features_,
            types_,
            netflix,
            load_,
            match,
            daemon,
            openvpn,
            protocol,
        )
        assert False
    except connect.ConnectError as error:
        assert str(error) == "No server found to establish a connection."

    # assert
    mocked_con_spec.assert_not_called()
    mocked_servers.assert_called_once()
    mocked_filter.assert_called_once_with(
        servers_fix, netflix, countries_, areas_, features_, types_, load_, match
    )
    mocked_best.assert_called_once_with(servers_fix)
    mocked_run.assert_called()


def test_openvpn_command_panic_error_when_no_message_given():
    # setup
    problem = "Test problem"

    # run
    panic = connect.OpenvpnCommandPanic(problem)

    # assert
    assert panic.problem == problem
    assert str(panic) == "Running openvpn failed: {}".format(problem)


def test_openvpn_command_add_openvpn_cmd_option_with_flag(openvpn_command_no_options):
    # setup
    flag = "--test"
    arg1 = "me"
    arg2 = "again"

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._add_openvpn_cmd_option(flag, arg1, arg2)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", flag, arg1, arg2]


def test_openvpn_command_add_openvpn_cmd_option_with_argument(
    openvpn_command_no_options
):
    # setup
    flag = "test"

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._add_openvpn_cmd_option(flag)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", flag]


def test_format_flag(openvpn_command_no_options):
    # setup
    flag = "test"
    expected_result = "--test"

    # run
    # pylint: disable=protected-access
    actual_result = openvpn_command_no_options._format_flag(flag)

    # assert
    assert actual_result == expected_result


def test_forge_number(openvpn_command_no_options):
    # setup
    key = "test"
    value = 3

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_number(key, value)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", "--test", str(value)]


def test_forge_string_no_auth_user_pass(openvpn_command_no_options):
    # setup
    key = "test"
    value = "value"

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_string(key, value)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", "--test", value]


def test_forge_string_when_auth_user_pass_no_builtin(openvpn_command_no_options):
    # setup
    key = "auth-user-pass"
    value = "/some/path"

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_string(key, value)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", "--auth-user-pass", value]


def test_forge_string_when_auth_user_pass_value_is_builtin(
    openvpn_command_no_options, mocker
):
    # setup
    key = "auth-user-pass"
    value = "built-in"
    path = "/some/path/creds"
    mocked_creds = mocker.patch(
        "connord.connect.resources.get_credentials_file", return_value=path
    )

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_string(key, value)

    # assert
    mocked_creds.assert_called_once()
    assert openvpn_command_no_options.cmd == ["openvpn", "--auth-user-pass", path]


def test_forge_bool_when_true(openvpn_command_no_options):
    # setup
    key = "test"
    values = [True, "True", "true"]

    for value in values:
        # run
        # pylint: disable=protected-access
        openvpn_command_no_options._forge_bool(key, value)
        # assert
        assert openvpn_command_no_options.cmd == ["openvpn", "--test"]
        openvpn_command_no_options.cmd = ["openvpn"]


def test_forge_bool_when_false(openvpn_command_no_options):
    # setup
    key = "test"
    values = [False, "False", "false", "something"]

    for value in values:
        # run
        # pylint: disable=protected-access
        openvpn_command_no_options._forge_bool(key, value)
        # assert
        assert openvpn_command_no_options.cmd == ["openvpn"]
        openvpn_command_no_options.cmd = ["openvpn"]


def test_forge_list_when_list_is_empty(openvpn_command_no_options):
    # setup
    key = "test"
    list_ = []

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_list(key, list_)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", "--test"]


def test_forge_list_when_list_has_values(openvpn_command_no_options):
    # setup
    key = "test"
    list_ = ["value", "other"]

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_list(key, list_)

    # assert
    assert openvpn_command_no_options.cmd == ["openvpn", "--test", "value", "other"]


def test_forget_list_when_key_is_scripts(openvpn_command_no_options):
    # setup
    key = "scripts"
    list_ = [{"name": "up", "path": "/some/path", "stage": "up", "creates": "test"}]

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_list(key, list_)

    assert openvpn_command_no_options.cmd == ["openvpn", "--up", "'/some/path' test"]


def test_format_script_arg_when_path_is_builtin(mocker, openvpn_command_no_options):
    # setup
    script_name = "somethin"
    path = "built-in"
    file_ = "somethin.env"
    script_path = "/path/to/script"
    env_dir = "/path/env"

    mocked_resources = mocker.patch("connord.connect.resources")
    mocked_resources.get_scripts_file.return_value = script_path
    mocked_resources.get_stats_dir.return_value = env_dir

    expected_result = "'{}' {}/{}".format(script_path, env_dir, file_)

    # run
    # pylint: disable=protected-access
    actual_result = openvpn_command_no_options._format_script_arg(
        script_name, path, file_
    )

    assert expected_result == actual_result


def test_forge_scripts_when_name_is_ipchange(openvpn_command_no_options):
    # setup
    scripts = [
        {"name": "ipchange", "path": "/my/path", "stage": "all", "creates": "test"}
    ]

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_scripts(scripts)

    # assert
    assert openvpn_command_no_options.cmd == [
        "openvpn",
        "--ipchange",
        "'/my/path' test",
    ]


def test_forge_scripts_when_name_is_unknown(openvpn_command_no_options):
    # setup
    scripts = [
        {"name": "something", "path": "/my/path", "stage": "all", "creates": "test"}
    ]

    # run
    # pylint: disable=protected-access
    openvpn_command_no_options._forge_scripts(scripts)

    # assert
    assert openvpn_command_no_options.cmd == [
        "openvpn",
        "--something",
        "'/my/path' test",
    ]


def test_forge_scripts_when_name_is_unknown_path_is_built_in(
    openvpn_command_no_options
):
    # setup
    scripts = [
        {"name": "something", "path": "built-in", "stage": "all", "creates": "test"}
    ]

    # run
    # pylint: disable=protected-access
    try:
        openvpn_command_no_options._forge_scripts(scripts)
        assert False
    except ResourceNotFoundError as error:
        assert str(error) == "No built-in found for 'something'."
