#!/usr/bin/env python

from connord import update


def set_up(mocker):
    mocked_user = mocker.patch("connord.iptables.user.is_root")
    mocked_user.return_value = True


def test_update_orig_when_zip_file_not_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    set_up(mocker)

    import importlib

    importlib.reload(update)

    mocked_shutil = mocker.patch("connord.update.move")
    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_file")
    from connord import resources

    mocked_zip_file.side_effect = resources.ResourceNotFoundError(zippath)

    try:
        update.update_orig()
    except resources.ResourceNotFoundError:
        assert False

    mocked_shutil.assert_not_called()


def test_update_orig_when_zip_file_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.zip.orig"
    set_up(mocker)
    import importlib

    importlib.reload(update)

    mocked_shutil = mocker.patch("connord.update.move")
    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_file")

    mocked_zip_file.return_value = zippath

    update.update_orig()

    mocked_shutil.assert_called_once_with(zippath, origpath)


def test_get(requests_mock, mocker):
    url = "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip"
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"

    mocker.patch("connord.update.update_orig")
    requests_mock.get(url, text="testing")

    mocked_open = mocker.patch("connord.update.open", mocker.mock_open(), create=True)

    mocked_zip_path = mocker.patch("connord.update.resources.get_zip_path")
    mocked_zip_path.return_value = zippath

    update.get()

    mocked_open.assert_called_with(zippath, "wb")


def test_uptodate_when_orig_zipfile_not_exists(mocker):
    origpath = "/etc/openvpn/client/nordvpn/ovpn.zip.orig"
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.side_effect = [False, True]

    retval = update.file_equals(origpath, zippath)

    expected_calls = [mocker.call(origpath)]
    actual_calls = mocked_os.path.exists.call_args_list
    assert actual_calls == expected_calls
    assert not retval


def test_uptodate_when_orig_file_exists_zip_file_not_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.side_effect = [True, False]

    retval = update.file_equals(origpath, zippath)

    expected_calls = [mocker.call(origpath), mocker.call(zippath)]
    actual_calls = mocked_os.path.exists.call_args_list
    assert actual_calls == expected_calls
    assert not retval


def test_uptodate_when_both_files_exist_sizes_are_not_equal(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.zip.orig"
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.side_effect = [True, True]
    mocked_os.path.getsize.side_effect = [100, 99]

    retval = update.file_equals(origpath, zippath)

    expected_calls = [mocker.call(origpath), mocker.call(zippath)]
    actual_calls = mocked_os.path.getsize.call_args_list
    assert actual_calls == expected_calls
    assert not retval


def test_uptodate_when_both_files_exist_sizes_are_equal(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.side_effect = [True, True]
    mocked_os.path.getsize.side_effect = [100, 100]

    retval = update.file_equals(origpath, zippath)

    expected_exists_calls = [mocker.call(origpath), mocker.call(zippath)]
    actual_exists_calls = mocked_os.path.exists.call_args_list

    expected_getsize_calls = [mocker.call(origpath), mocker.call(zippath)]
    actual_getsize_calls = mocked_os.path.getsize.call_args_list

    assert actual_getsize_calls == expected_getsize_calls
    assert actual_exists_calls == expected_exists_calls
    assert retval


def test_update_needed_when_zipfile_not_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.return_value = False
    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_file")
    from connord import resources

    mocked_zip_file.side_effect = resources.ResourceNotFoundError(zippath)

    retval = update.update_needed()

    mocked_zip_file.assert_called_once()
    assert retval


def test_update_needed_when_zipfile_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    mocker.patch("connord.update.TIMEOUT", 4)

    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_file")
    mocked_zip_file.return_value = zippath

    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.getctime.return_value = 5

    mocked_datetime = mocker.patch("connord.update.datetime")
    mocked_datetime.now.return_value = 10
    mocked_datetime.fromtimestamp.return_value = 5

    retval = update.update_needed()

    mocked_datetime.now.assert_called_once()
    mocked_os.path.getctime.assert_called_with(zippath)
    mocked_datetime.fromtimestamp.assert_called_once_with(5)
    assert retval


def test_update_when_force_is_true(mocker):
    mocked_get = mocker.patch.object(update, "get")
    mocked_unzip = mocker.patch.object(update, "unzip")

    retval = update.update(True)

    mocked_get.assert_called_once()
    mocked_unzip.assert_called_once()
    assert retval


def test_update_when_force_is_false_files_are_updated(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.zip.orig"

    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_path")
    mocked_zip_file.side_effect = [zippath, origpath]

    mocked_get = mocker.patch.object(update, "get")
    mocked_update_needed = mocker.patch.object(update, "update_needed")
    mocked_update_needed.return_value = True
    mocked_file_equals = mocker.patch.object(update, "file_equals")
    mocked_file_equals.return_value = False
    mocked_unzip = mocker.patch.object(update, "unzip")

    retval = update.update(False)

    mocked_get.assert_called_once()
    mocked_update_needed.assert_called_once()
    mocked_file_equals.assert_called_once_with(origpath, zippath)
    mocked_unzip.assert_called_once()
    assert retval


def test_update_when_force_is_false_files_are_uptodate(capsys, mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.zip.orig"

    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_path")
    mocked_zip_file.side_effect = [zippath, origpath]

    mocked_get = mocker.patch.object(update, "get")
    mocked_update_needed = mocker.patch.object(update, "update_needed")
    mocked_update_needed.return_value = True
    mocked_file_equals = mocker.patch.object(update, "file_equals")
    mocked_file_equals.return_value = True
    mocked_unzip = mocker.patch.object(update, "unzip")

    retval = update.update(False)

    captured = capsys.readouterr()

    mocked_get.assert_called_once()
    mocked_update_needed.assert_called_once()
    mocked_file_equals.assert_called_once_with(origpath, zippath)
    mocked_unzip.assert_not_called()
    assert retval
    assert captured.out == zippath + " already up-to-date\n"


def test_update_when_force_is_false_no_update_needed(capsys, mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.zip.orig"

    mocked_zip_file = mocker.patch("connord.update.resources.get_zip_path")
    mocked_zip_file.side_effect = [zippath, origpath]

    mocked_update_needed = mocker.patch.object(update, "update_needed")
    mocked_update_needed.return_value = False
    mocked_datetime = mocker.patch("connord.update.datetime")
    mocked_datetime.fromtimestamp.return_value = 5
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.getctime.return_value = 5
    mocker.patch("connord.update.TIMEOUT", 4)

    retval = update.update(False)

    mocked_update_needed.assert_called_once()
    mocked_os.path.getctime.assert_called_once_with(zippath)
    mocked_datetime.fromtimestamp.assert_called_once_with(5)
    captured = capsys.readouterr()

    assert retval
    assert captured.out == "No update needed. Next update needed at 9\n"


class MockZipFile:
    def __init__(self):
        self.dir_ = ""

    def extractall(self, zdir):
        self.dir_ = zdir


def test_unzip(capsys, mocker):
    # setup
    mocked_resources = mocker.patch("connord.update.resources")
    mocked_resources.get_zip_dir.return_value = "/test"
    mocked_resources.get_zip_file.return_value = "/test/ovpn.zip"
    mocked_zip_file = mocker.patch("connord.update.ZipFile")
    zip_file_mock = MockZipFile()
    mocked_zip_file.return_value.__enter__.return_value = zip_file_mock

    # run
    update.unzip()

    # assert
    captured = capsys.readouterr()
    assert zip_file_mock.dir_ == "/test"
    assert captured.out == "Unzipping /test/ovpn.zip ...\n"
    assert captured.err == ""
