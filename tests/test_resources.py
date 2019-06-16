# pylint: disable=too-many-lines
from connord import resources
from main_test_module import MockBase


def _mock_os_any(mocker, func, return_value):
    if func:
        result = "connord.resources.os." + func
        return mocker.patch(result, return_value=return_value)

    return mocker.patch("connord.resources.os")


def _mock_os(mocker):
    return mocker.patch("connord.resources.os")


def _mock_get_zip_dir(mocker):
    return mocker.patch("connord.resources.get_zip_dir")


def _mock_open(mocker):
    return mocker.patch("connord.resources.open", mocker.mock_open(), create=True)


def _setup():
    import importlib

    importlib.reload(resources)


def _mock_get_username(mocker, return_value):
    return mocker.patch("connord.resources._get_username", return_value=return_value)


def _mock_getpass(mocker, return_value):
    return mocker.patch("connord.resources.getpass.getpass", return_value=return_value)


def _mock_user_is_root(mocker, return_value):
    return mocker.patch("connord.resources.user.is_root", return_value=return_value)


def _mock_get_ovpn_dir(mocker, return_value):
    return mocker.patch("connord.resources.get_ovpn_dir", return_value=return_value)


def _mock_get_ovpn_protocol_dir(mocker, return_value):
    return mocker.patch(
        "connord.resources.get_ovpn_protocol_dir", return_value=return_value
    )


def _mock_get_scripts_dir(mocker, return_value):
    return mocker.patch("connord.resources.get_scripts_dir", return_value=return_value)


def _mock_get_config_dir(mocker, return_value):
    return mocker.patch("connord.resources.get_config_dir", return_value=return_value)


def _mock_get_config_file(mocker, return_value):
    return mocker.patch("connord.resources.get_config_file", return_value=return_value)


def _mock_get_stats_dir(mocker, return_value):
    return mocker.patch("connord.resources.get_stats_dir", return_value=return_value)


def _mock_get_stats_file(mocker, return_value):
    return mocker.patch("connord.resources.get_stats_file", return_value=return_value)


def test_resource_not_found_error_without_message(mocker):
    # setup
    test_file = "test_file"
    mocked_zip_path = mocker.patch("connord.resources.get_zip_path")
    mocked_zip_path.side_effect = resources.ResourceNotFoundError(test_file)

    # run and assert
    try:
        resources.get_zip_path()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == test_file
        assert str(error) == "Resource does not exist: {!r}".format(test_file)


def test_resource_not_found_error_with_message(mocker):
    # setup
    test_file = "test_file"
    test_message = "test_message"
    mocked_zip_path = mocker.patch("connord.resources.get_zip_path")
    mocked_zip_path.side_effect = resources.ResourceNotFoundError(
        test_file, test_message
    )

    # run and assert
    try:
        resources.get_zip_path()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == test_file
        assert str(error) == "test_message"


def test_resource_not_found_error_when_resource_file_is_none(mocker):
    # setup
    test_file = None
    test_message = "test_message"
    mocked_zip_path = mocker.patch("connord.resources.get_zip_path")
    mocked_zip_path.side_effect = resources.ResourceNotFoundError(
        test_file, test_message
    )

    # run and assert
    try:
        resources.get_zip_path()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == test_file
        assert str(error) == test_message


def test_get_zip_dir_when_create_is_false_path_exists(mocker):
    # setup
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = True

    expected_result = "/etc/openvpn/client/nordvpn"

    # run
    actual_result = resources.get_zip_dir(create=False)

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_zip_dir_when_create_is_true_path_exists(mocker):
    # setup
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = True

    expected_result = "/etc/openvpn/client/nordvpn"

    # run
    actual_result = resources.get_zip_dir(create=True)

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_os.makedirs.assert_not_called()
    assert actual_result == expected_result


def test_get_zip_dir_when_create_is_true_path_not_exists(mocker):
    # setup
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    expected_result = "/etc/openvpn/client/nordvpn"

    # run
    actual_result = resources.get_zip_dir(create=True)

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_os.makedirs.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_zip_dir_when_create_is_false_path_not_exists(mocker):
    # setup
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    expected_result = "/etc/openvpn/client/nordvpn"

    # run
    try:
        resources.get_zip_dir(create=False)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_os.makedirs.assert_not_called()


def test_get_zip_path_when_parameter_is_default(mocker):
    # setup
    test_zip_dir = "/test/dir"
    mocked_get_zip_dir = _mock_get_zip_dir(mocker)
    mocked_get_zip_dir.return_value = test_zip_dir
    expected_result = "/test/dir/ovpn.zip"

    # run
    actual_result = resources.get_zip_path()

    # assert
    mocked_get_zip_dir.assert_called_once_with(create=False)
    assert actual_result == expected_result


def test_get_zip_path_when_parameter_is_string(mocker):
    # setup
    test_zip_dir = "/test/dir"
    test_zip_name = "test.zip"
    mocked_get_zip_dir = _mock_get_zip_dir(mocker)
    mocked_get_zip_dir.return_value = test_zip_dir
    expected_result = "/test/dir/test.zip"

    # run
    actual_result = resources.get_zip_path(zip_name=test_zip_name)

    # assert
    mocked_get_zip_dir.assert_called_once()
    assert actual_result == expected_result


def test_get_zip_file_when_default_parameters_path_exists(mocker):
    # setup
    test_zip_dir = "/test/dir"
    mocked_get_zip_dir = _mock_get_zip_dir(mocker)
    mocked_get_zip_dir.return_value = test_zip_dir
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = True
    expected_result = "/test/dir/ovpn.zip"

    # run
    actual_result = resources.get_zip_file()

    # assert
    mocked_get_zip_dir.assert_called_once_with(create=True)
    mocked_os.path.exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_zip_file_when_default_parameters_path_not_exists(mocker):
    # setup
    test_zip_dir = "/test/dir"
    mocked_get_zip_dir = _mock_get_zip_dir(mocker)
    mocked_get_zip_dir.return_value = test_zip_dir
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False
    expected_result = "/test/dir/ovpn.zip"

    # run
    try:
        resources.get_zip_file()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_get_zip_dir.assert_called_once_with(create=True)
    mocked_os.path.exists.assert_called_once_with(expected_result)


def test_get_database_file_when_default(mocker):
    # setup
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False
    mocked_open = _mock_open(mocker)
    expected_result = "/test/data.base"
    # pylint: disable=protected-access
    resources.__DATABASE_FILE = expected_result

    # run
    actual_result = resources.get_database_file()

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_open.assert_called_once_with(expected_result, "w")
    assert actual_result == expected_result


def test_get_database_file_when_create_is_false(mocker):
    # setup
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False
    mocked_open = _mock_open(mocker)
    expected_result = "/test/data.base"
    # pylint: disable=protected-access
    resources.__DATABASE_FILE = expected_result

    # run
    try:
        resources.get_database_file(create=False)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_open.assert_not_called()


def test_file_has_permissions_good(mocker):
    # setup
    from collections import namedtuple

    test_path = "/test/dir/file.name"
    test_stat_result = namedtuple("stat_result", ["st_mode"])
    test_stat_result.st_mode = 33152
    mocked_stat = mocker.patch("connord.resources.os.stat")
    mocked_stat.return_value = test_stat_result

    # run
    result = resources.file_has_permissions(test_path)

    # assert
    mocked_stat.assert_called_once_with(test_path)
    assert result


def test_file_has_permissions_bad(mocker):
    # setup
    from collections import namedtuple

    test_path = "/test/dir/file.name"
    test_stat_result = namedtuple("stat_result", ["st_mode"])
    test_stat_result.st_mode = 33188
    mocked_stat = mocker.patch("connord.resources.os.stat")
    mocked_stat.return_value = test_stat_result

    # run
    result = resources.file_has_permissions(test_path)

    # assert
    mocked_stat.assert_called_once_with(test_path)
    assert not result


def test_verify_file_permissions_good(mocker):
    # setup
    test_path = "/test/dir/file.name"
    mocked_file_has_perm = mocker.patch(
        "connord.resources.file_has_permissions", return_value=True
    )

    # run
    result = resources.verify_file_permissions(test_path)

    # assert
    mocked_file_has_perm.assert_called_once_with(test_path, 0o600)
    assert result


def test_verify_file_permissions_bad(mocker):
    # setup
    test_path = "/test/dir/file.name"
    mocked_file_has_perm = mocker.patch(
        "connord.resources.file_has_permissions", return_value=False
    )

    # run
    try:
        resources.verify_file_permissions(test_path)
        assert False
    except PermissionError as error:
        assert (
            str(error)
            # pylint: disable=line-too-long
            == "Unsafe file permissions: '/test/dir/file.name' should have mode: '0o600'."
        )

    # assert
    mocked_file_has_perm.assert_called_once_with(test_path, 0o600)


def test_get_credentials_dir_default_params_dir_not_exists(mocker):
    # setup
    _setup()
    expected_result = "/test/dir"
    # pylint: disable=protected-access
    resources.__NORDVPN_DIR = expected_result
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    # run
    actual_result = resources.get_credentials_dir()

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_os.makedirs.assert_called_once_with(expected_result, mode=0o755)
    assert actual_result == expected_result


def test_get_credentials_dir_create_is_false_dir_not_exists(mocker):
    # setup
    _setup()
    expected_result = "/test/dir"
    # pylint: disable=protected-access
    resources.__NORDVPN_DIR = expected_result
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    # run
    try:
        resources.get_credentials_dir(create=False)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_os.makedirs.assert_not_called()


def test_get_credentials_file_default_params_path_not_exists(mocker):
    # setup
    _mock_user_is_root(mocker, return_value=True)
    _setup()
    mocked_creds_dir = mocker.patch(
        "connord.resources.get_credentials_dir", return_value="/test/dir"
    )
    expected_result = "/test/dir/credentials"
    mocked_create_creds_file = mocker.patch("connord.resources.create_credentials_file")
    mocked_verify = mocker.patch("connord.resources.verify_file_permissions")
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    # run
    actual_result = resources.get_credentials_file()

    # assert
    mocked_creds_dir.assert_called_once()
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_create_creds_file.assert_called_once_with(expected_result)
    mocked_verify.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_credentials_file_create_false_path_not_exists(mocker):
    # setup
    _mock_user_is_root(mocker, return_value=True)
    _setup()
    mocked_creds_dir = mocker.patch(
        "connord.resources.get_credentials_dir", return_value="/test/dir"
    )
    expected_result = "/test/dir/credentials"
    mocked_create_creds_file = mocker.patch("connord.resources.create_credentials_file")
    mocked_verify = mocker.patch("connord.resources.verify_file_permissions")
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    # run
    try:
        resources.get_credentials_file(create=False)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_creds_dir.assert_called_once()
    mocked_os.path.exists.assert_called_once_with(expected_result)
    mocked_create_creds_file.assert_not_called()
    mocked_verify.assert_not_called()


def test_create_credentials_file(mocker):
    # setup
    _setup()
    expected_user_name = "test name"
    expected_result = "/test/dir/creds"
    mocked_get_username = _mock_get_username(mocker, expected_user_name)
    mocked_getpass = _mock_getpass(mocker, "password")
    mocked_open = _mock_open(mocker)
    mocked_os = _mock_os(mocker)

    # run
    actual_result = resources.create_credentials_file(expected_result)

    # assert
    mocked_get_username.assert_called_once()
    mocked_getpass.assert_called_once_with("Enter password: ")
    mocked_open.assert_called_once_with(expected_result, "w")
    mocked_os.chmod.assert_called_once_with(expected_result, mode=0o600)
    assert actual_result == expected_result


def test_get_ovpn_dir_when_dir_not_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    expected_result = "/test/dir"
    # pylint: disable=protected-access
    resources.__NORDVPN_DIR = expected_result
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = False

    # run
    try:
        resources.get_ovpn_dir()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    mocked_os.path.exists.assert_called_once_with(expected_result)


def test_get_ovpn_dir_when_dir_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    expected_result = "/test/dir"
    # pylint: disable=protected-access
    resources.__NORDVPN_DIR = expected_result
    mocked_os = _mock_os(mocker)
    mocked_os.path.exists.return_value = True

    # run
    actual_result = resources.get_ovpn_dir()

    mocked_os.path.exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_ovpn_protocol_dir_when_default_path_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    mocked_get_ovpn_dir = _mock_get_ovpn_dir(mocker, "/test/dir")
    expected_result = "/test/dir/ovpn_udp"
    mocked_exists = _mock_os_any(mocker, "path.exists", True)

    # run
    actual_result = resources.get_ovpn_protocol_dir()

    # assert
    mocked_get_ovpn_dir.assert_called_once()
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_ovpn_protocol_dir_when_default_and_path_not_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    mocked_get_ovpn_dir = _mock_get_ovpn_dir(mocker, "/test/dir")
    expected_result = "/test/dir/ovpn_udp"
    mocked_exists = _mock_os_any(mocker, "path.exists", False)

    # run
    try:
        resources.get_ovpn_protocol_dir()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_get_ovpn_dir.assert_called_once()
    mocked_exists.assert_called_once_with(expected_result)


def test_get_ovpn_config_when_domain_without_fqdn_and_path_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    mocked_get_dir = _mock_get_ovpn_protocol_dir(mocker, "/test/dir/ovpn_udp")
    domain = "us2000"
    protocol = "udp"
    expected_result = "/test/dir/ovpn_udp/" + domain + ".nordvpn.com.udp.ovpn"
    mocked_exists = _mock_os_any(mocker, "path.exists", True)

    # run with defaults
    actual_result = resources.get_ovpn_config(domain)

    # assert
    mocked_get_dir.assert_called_once_with(protocol)
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_ovpn_config_when_domain_with_fqdn_and_path_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    mocked_get_dir = _mock_get_ovpn_protocol_dir(mocker, "/test/dir/ovpn_udp")
    domain = "us2000.nordvpn.com"
    protocol = "udp"
    expected_result = "/test/dir/ovpn_udp/" + domain + ".udp.ovpn"
    mocked_exists = _mock_os_any(mocker, "path.exists", True)

    # run with defaults
    actual_result = resources.get_ovpn_config(domain)

    # assert
    mocked_get_dir.assert_called_once_with(protocol)
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_ovpn_config_when_path_not_exists(mocker):
    # setup
    _mock_user_is_root(mocker, True)
    _setup()
    mocked_get_dir = _mock_get_ovpn_protocol_dir(mocker, "/test/dir/ovpn_udp")
    domain = "us2000.nordvpn.com"
    protocol = "udp"
    expected_result = "/test/dir/ovpn_udp/" + domain + ".udp.ovpn"
    mocked_exists = _mock_os_any(mocker, "path.exists", False)

    # run with defaults
    try:
        resources.get_ovpn_config(domain)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_get_dir.assert_called_once_with(protocol)
    mocked_exists.assert_called_once_with(expected_result)


def test_get_scripts_dir_when_path_exists(mocker):
    # setup
    _setup()
    # pylint: disable=protected-access
    resources.__SCRIPTS_DIR = "/test/dir"
    mockbase = MockBase("resources")
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", True)
    expected_result = "/test/dir"

    # run
    actual_result = resources.get_scripts_dir()

    # assert
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_scripts_dir_when_path_not_exists(mocker):
    # setup
    _setup()
    # pylint: disable=protected-access
    resources.__SCRIPTS_DIR = "/test/dir"
    mockbase = MockBase("resources")
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    expected_result = "/test/dir"
    mocked_filename = mockbase.mock_resource_filename(mocker, expected_result)

    # run
    actual_result = resources.get_scripts_dir()

    # assert
    mocked_exists.assert_called_once_with(expected_result)
    mocked_filename.assert_called_once()
    assert actual_result == expected_result


def test_get_scripts_file_when_path_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    mocked_scripts_dir = _mock_get_scripts_dir(mocker, "/test/dir")
    expected_result = "/test/dir/openvpn_up_down.bash"
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", True)

    # run
    actual_result = resources.get_scripts_file()

    # assert
    mocked_scripts_dir.assert_called_once()
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_scripts_file_when_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    mocked_scripts_dir = _mock_get_scripts_dir(mocker, "/test/dir")
    expected_result = "/test/dir/openvpn_up_down.bash"
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)

    # run
    try:
        resources.get_scripts_file()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_scripts_dir.assert_called_once()
    mocked_exists.assert_called_once_with(expected_result)


def test_get_config_dir_when_path_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    expected_result = "/test/dir"
    # pylint: disable=protected-access
    resources.__CONFIG_DIR = expected_result
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", True)

    # run
    actual_result = resources.get_config_dir()

    # assert
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_config_dir_when_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    expected_result = "/test/other/dir/config"
    # pylint: disable=protected-access
    resources.__CONFIG_DIR = "/test/dir"
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    mocked_filename = mockbase.mock_resource_filename(mocker, expected_result)

    # run
    actual_result = resources.get_config_dir()

    # assert
    mocked_exists.assert_called_once_with("/test/dir")
    mocked_filename.assert_called_once()
    assert actual_result == expected_result


def test_list_config_dir_when_filetype_is_none_and_list_has_files(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    test_dir = "/test/dir"
    mocked_config_dir = _mock_get_config_dir(mocker, test_dir)
    # pylint: disable=protected-access
    dir_list = ["some", "other"]
    mocked_listdir = mockbase.mock_os_any(mocker, "listdir", dir_list)
    expected_list = [test_dir + "/" + _file for _file in dir_list]

    # run
    actual_list = resources.list_config_dir()

    # assert
    mocked_config_dir.assert_called_once()
    mocked_listdir.assert_called_once_with("/test/dir")
    assert actual_list == expected_list


def test_list_config_dir_when_filetype_is_none_and_list_has_no_files(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    test_dir = "/test/dir"
    mocked_config_dir = _mock_get_config_dir(mocker, test_dir)
    dir_list = list()
    mocked_listdir = mockbase.mock_os_any(mocker, "listdir", dir_list)

    # run
    actual_list = resources.list_config_dir()

    # assert
    mocked_config_dir.assert_called_once()
    mocked_listdir.assert_called_once_with("/test/dir")
    assert not actual_list


def test_list_config_dir_when_filetype_is_set_and_list_has_no_files(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    test_dir = "/test/dir"
    mocked_config_dir = _mock_get_config_dir(mocker, test_dir)
    dir_list = list()
    mocked_listdir = mockbase.mock_os_any(mocker, "listdir", dir_list)

    # run
    actual_list = resources.list_config_dir(filetype=".txt")

    # assert
    mocked_config_dir.assert_called_once()
    mocked_listdir.assert_called_once_with("/test/dir")
    assert not actual_list


def test_get_config_file_when_path_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    test_dir = "/test/dir"
    mocked_config_dir = _mock_get_config_dir(mocker, test_dir)
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", True)
    expected_result = test_dir + "/config.yml"

    # run
    actual_result = resources.get_config_file()

    # assert
    mocked_config_dir.assert_called_once()
    mocked_exists.assert_called_once_with(expected_result)
    assert actual_result == expected_result


def test_get_config_file_when_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    test_dir = "/test/dir"
    mocked_config_dir = _mock_get_config_dir(mocker, test_dir)
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    expected_result = test_dir + "/config.yml"

    # run and assert
    try:
        resources.get_config_file()
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    mocked_config_dir.assert_called_once()
    mocked_exists.assert_called_once_with(expected_result)


def test_get_config_when_valid_yaml(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    fixture = "tests/fixtures/config_valid_yaml_fixture.yml"
    import yaml

    with open(fixture, "r") as fix_fd:
        expected_result = yaml.safe_load(fix_fd)

    mocked_config_file = _mock_get_config_file(
        mocker, "tests/fixtures/config_valid_yaml_fixture.yml"
    )

    # run
    actual_result = resources.get_config()

    # assert
    mocked_config_file.assert_called_once()
    assert actual_result == expected_result


def test_get_config_when_invalid_yaml(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)
    yaml_fixture = "tests/fixtures/config_invalid_yaml_fixture.yml"

    mocked_config_file = _mock_get_config_file(mocker, yaml_fixture)

    # run and assert
    try:
        resources.get_config()
        assert False
    except resources.MalformedResourceError as error:
        assert error.resource_file == yaml_fixture
        assert error.problem == "expected <block end>, but found '-'"
        assert (
            error.problem_mark
            # pylint: disable=line-too-long
            == '  in "tests/fixtures/config_invalid_yaml_fixture.yml", line 4, column 3'
        )

    mocked_config_file.assert_called_once()


def test_write_config_when_valid_config(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources, create_tmpdir=True)

    config_file = mockbase.get_tmpdir() + "/config.yml"
    config = {"connord": ["value", "too", {"test": "value"}]}
    mocked_config_file = _mock_get_config_file(mocker, config_file)

    # run
    resources.write_config(config)

    # assert
    import os

    mocked_config_file.assert_called_once()
    assert os.path.exists(config_file)

    # tear down
    mockbase.tear_down()


def test_write_config_when_config_is_list_should_raise_type_error(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)

    config_file = mockbase.get_tmpdir() + "/config.yml"
    config = ["test"]
    mocked_config_file = _mock_get_config_file(mocker, config_file)

    # run and assert
    try:
        resources.write_config(config)
        assert False
    except TypeError:
        assert True

    mocked_config_file.assert_called_once()


def test_write_config_when_error_message(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.setup(resources)

    config_file = mockbase.get_tmpdir() + "/config.yml"
    config = ["test"]
    mocked_config_file = _mock_get_config_file(mocker, config_file)

    # run and assert
    try:
        resources.write_config(config)
        assert False
    except TypeError as error:
        assert str(
            error
            # pylint: disable=line-too-long
        ) == "Could not write to {!r}: Invalid type: Found <class 'list'> but expected <class 'dict'>.".format(
            config_file
        )

    mocked_config_file.assert_called_once()


def test_get_stats_dir_when_default_and_path_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_dir = "/run/dir"
    # pylint: disable=protected-access
    resources.__RUN_DIR = stats_dir

    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", True)
    mocked_makedirs = mockbase.mock_os_any(mocker, "makedirs", stats_dir)
    expected_result = stats_dir

    # run
    actual_result = resources.get_stats_dir()

    # assert
    mocked_exists.assert_called_once_with(stats_dir)
    mocked_makedirs.assert_not_called()

    assert actual_result == expected_result


def test_get_stats_dir_when_default_and_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_dir = "/run/dir"
    # pylint: disable=protected-access
    resources.__RUN_DIR = stats_dir

    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    mocked_makedirs = mockbase.mock_os_any(mocker, "makedirs", stats_dir)
    expected_result = stats_dir

    # run
    actual_result = resources.get_stats_dir()

    # assert
    mocked_exists.assert_called_once_with(stats_dir)
    mocked_makedirs.assert_called_once_with(stats_dir, mode=0o750)

    assert actual_result == expected_result


def test_get_stats_dir_when_create_is_false_and_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_dir = "/run/dir"
    # pylint: disable=protected-access
    resources.__RUN_DIR = stats_dir

    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    mocked_makedirs = mockbase.mock_os_any(mocker, "makedirs", stats_dir)
    expected_result = stats_dir

    # run
    try:
        resources.get_stats_dir(create=False)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_exists.assert_called_once_with(stats_dir)
    mocked_makedirs.assert_not_called()


def test_get_stats_file_when_default_and_path_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_dir = "/run/dir"

    mocked_stats_dir = _mock_get_stats_dir(mocker, stats_dir)
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", True)
    mocked_open = mockbase.mock_open(mocker)
    expected_result = stats_dir + "/stats"

    # run
    actual_result = resources.get_stats_file()

    # assert
    mocked_stats_dir.assert_called_once_with(True)
    mocked_exists.assert_called_once_with(expected_result)
    mocked_open.assert_not_called()

    assert actual_result == expected_result


def test_get_stats_file_when_default_and_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_dir = "/run/dir"

    mocked_stats_dir = _mock_get_stats_dir(mocker, stats_dir)
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    mocked_open = mockbase.mock_open(mocker)
    expected_result = stats_dir + "/stats"

    # run
    actual_result = resources.get_stats_file()

    # assert
    mocked_stats_dir.assert_called_once_with(True)
    mocked_exists.assert_called_once_with(expected_result)
    mocked_open.assert_called_once_with(expected_result, "w")

    assert actual_result == expected_result


def test_get_stats_file_when_create_is_false_and_path_not_exists(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_dir = "/run/dir"

    mocked_stats_dir = _mock_get_stats_dir(mocker, stats_dir)
    mocked_exists = mockbase.mock_os_any(mocker, "path.exists", False)
    mocked_open = mockbase.mock_open(mocker)
    expected_result = stats_dir + "/stats"

    # run
    try:
        resources.get_stats_file(create=False)
        assert False
    except resources.ResourceNotFoundError as error:
        assert error.resource_file == expected_result

    # assert
    mocked_stats_dir.assert_called_once_with(False)
    mocked_exists.assert_called_once_with(expected_result)
    mocked_open.assert_not_called()


def test_get_stats_when_valid_yaml(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_file = "tests/fixtures/config_valid_yaml_fixture.yml"
    mocked_stats_file = _mock_get_stats_file(mocker, stats_file)
    import yaml

    with open(stats_file) as stats_fd:
        expected_result = yaml.safe_load(stats_fd)

    # run
    actual_result = resources.get_stats()

    # assert
    mocked_stats_file.assert_called_once()
    assert actual_result == expected_result


def test_get_stats_when_invalid_yaml(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_file = "tests/fixtures/config_invalid_yaml_fixture.yml"
    mocked_stats_file = _mock_get_stats_file(mocker, stats_file)

    # run
    try:
        resources.get_stats()
    except resources.MalformedResourceError as error:
        assert error.resource_file == stats_file
        assert error.problem == "expected <block end>, but found '-'"
        assert (
            error.problem_mark
            # pylint: disable=line-too-long
            == '  in "tests/fixtures/config_invalid_yaml_fixture.yml", line 4, column 3'
        )

    # assert
    mocked_stats_file.assert_called_once()


def test_get_stats_when_stats_dict_is_none(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources)

    stats_file = "tests/fixtures/config_valid_yaml_fixture.yml"
    mocked_stats_file = _mock_get_stats_file(mocker, stats_file)
    mocked_safe_load = mocker.patch(
        "connord.resources.yaml.safe_load", return_value=None
    )
    expected_result = dict()

    # run
    actual_result = resources.get_stats()

    # assert
    mocked_stats_file.assert_called_once()
    mocked_safe_load.assert_called_once()
    assert actual_result == expected_result


def test_write_stats_when_valid_dict(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources, create_tmpdir=True)

    stats_file = mockbase.get_tmpdir() + "/stats"
    stats = {"connord": ["value", "too", {"test": "value"}]}
    mocked_stats_file = _mock_get_stats_file(mocker, stats_file)

    # run
    resources.write_stats(stats)

    # assert
    import os

    mocked_stats_file.assert_called_once()
    assert os.path.exists(stats_file)

    # tear down
    mockbase.tear_down()


def test_write_stats_when_invalid_dict(mocker):
    # setup
    mockbase = MockBase("resources")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(resources, create_tmpdir=True)

    stats_file = "/test/stats"
    stats = list()
    mocked_stats_file = _mock_get_stats_file(mocker, stats_file)

    # run
    try:
        resources.write_stats(stats)
    except TypeError as error:
        assert str(
            error
            # pylint: disable=line-too-long
        ) == "Could not write to {!r}: Invalid type: Found <class 'list'> but expected <class 'dict'>.".format(
            stats_file
        )

    # assert
    mocked_stats_file.assert_called_once()
