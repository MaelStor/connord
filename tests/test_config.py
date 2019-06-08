# vim: set fileencoding=utf-8 :

from connord import config


def test_it_get_config():
    assert isinstance(config.get_config(), dict)


def test_get_config_file_when_global_config_file_exists(mocker):
    mocked_os = mocker.patch("connord.config.os")
    mocked_os.path.exists.return_value = True

    actual_config_file = config.get_config_file()
    expected_config_file = "/etc/connord/config.yml"

    assert expected_config_file == actual_config_file


def test_get_config_file_when_global_config_file_not_exists(mocker):
    mocked_os = mocker.patch("connord.config.os")
    mocked_os.path.exists.return_value = False

    actual_config_file = config.get_config_file()

    assert actual_config_file.endswith("connord/config/config.yml")
