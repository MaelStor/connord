# vim: set fileencoding=utf-8 :

from connord import resources


def test_it_get_config():
    assert isinstance(resources.get_config(), dict)


def test_get_config_file_when_global_config_file_exists(mocker):
    mocked_os = mocker.patch("connord.resources.os")
    mocked_os.path.exists.return_value = True

    actual_config_file = resources.get_config_file()
    expected_config_file = "/etc/connord/config.yml"

    assert expected_config_file == actual_config_file


def test_get_config_file_when_config_file_not_exists(mocker):
    mocked_os = mocker.patch("connord.resources.os")
    mocked_os.path.exists.return_value = False

    try:
        resources.get_config_file()
        assert False
    except resources.ResourceNotFoundError as error:
        actual_message = str(error)

    assert actual_message.startswith("Resource does not exist:")
