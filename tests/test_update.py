#!/usr/bin/env python

from connord import update


def test_update_orig_when_zip_file_not_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    mocked_os = mocker.patch("connord.update.os")
    mocked_shutil = mocker.patch("connord.update.move")

    mocked_os.path.exists.return_value = False
    update.update_orig()

    mocked_os.path.exists.assert_called_once_with(zippath)
    mocked_shutil.assert_not_called()


def test_update_orig_when_zip_file_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"

    mocked_os = mocker.patch("connord.update.os")
    mocked_shutil = mocker.patch("connord.update.move")

    mocked_os.path.exists_return_value = True
    mocked_shutil.return_value = True

    update.update_orig()

    mocked_os.path.exists.assert_called_once_with(zippath)
    mocked_shutil.assert_called_once_with(zippath, origpath)


def test_update_orig_when_zip_file_exists_move_is_success(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"

    mocked_os = mocker.patch("connord.update.os")
    mocked_shutil = mocker.patch("connord.update.move")

    mocked_os.path.exists_return_value = True
    mocked_shutil.return_value = True

    retval = update.update_orig()

    mocked_os.path.exists.assert_called_once_with(zippath)
    mocked_shutil.assert_called_once_with(zippath, origpath)
    assert retval


def test_get_when_update_orig_is_false(mocker):
    mocked_update = mocker.patch("connord.update.update_orig")
    mocked_update.return_value = False

    retval = update.get()

    mocked_update.assert_called_once()
    assert not retval


# def _setup_mock_response(status=200, content='testing', json_data=None,
#                          raise_for_status=None):
#     '''Helper function to create a mocked_response'''
#
#     mock_response = mock.MagicMock()
#     mock_response.raise_for_status = mock.Mock()
#     if raise_for_status:
#         mock_response.raise_for_status.side_effect = raise_for_status
#
#     mock_response.status_code = status
#     mock_response.content = content
#     mock_response.iter_content.return_value = content
#
#     if json_data:
#         mock_response.json = mock.Mock(return_value=json_data)
#
#     return mock_response


def test_get(requests_mock, mocker):
    url = "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip"
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"

    mocked_update_orig = mocker.patch("connord.update.update_orig")
    mocked_update_orig.return_value = True
    requests_mock.get(url, text="testing")

    mocked_open = mocker.patch("connord.update.open", mocker.mock_open(), create=True)

    update.get()

    mocked_open.assert_called_with(zippath, "wb")


def test_uptodate_when_orig_zipfile_not_exists(mocker):
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"
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
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"
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


# def test_unzip(mocker):
#     destdir = "/etc/openvpn/client/nordvpn"
#     mocked_zipfile = mocker.patch.object(update.ZipFile, "extractall")
#
#     update.unzip()
#     mocked_zipfile.assert_called_with(destdir)


def test_update_needed_when_zipfile_not_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.return_value = False

    retval = update.update_needed()

    mocked_os.path.exists.assert_called_with(zippath)
    assert retval


def test_update_needed_when_zipfile_exists(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    mocker.patch("connord.update.TIMEOUT", 4)

    mocked_os = mocker.patch("connord.update.os")
    mocked_os.path.exists.return_value = True
    mocked_os.path.getctime.return_value = 5

    mocked_datetime = mocker.patch("connord.update.datetime")
    mocked_datetime.now.return_value = 10
    mocked_datetime.fromtimestamp.return_value = 5

    retval = update.update_needed()

    mocked_os.path.exists.assert_called_once_with(zippath)
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
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"

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


def test_update_when_force_is_false_files_are_uptodate(mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"
    origpath = "/etc/openvpn/client/nordvpn/ovpn.orig.zip"

    mocked_get = mocker.patch.object(update, "get")
    mocked_update_needed = mocker.patch.object(update, "update_needed")
    mocked_update_needed.return_value = True
    mocked_file_equals = mocker.patch.object(update, "file_equals")
    mocked_file_equals.return_value = True
    mocked_unzip = mocker.patch.object(update, "unzip")

    retval = update.update(False)

    mocked_get.assert_called_once()
    mocked_update_needed.assert_called_once()
    mocked_file_equals.assert_called_once_with(origpath, zippath)
    mocked_unzip.assert_not_called()
    assert retval


def test_update_when_force_is_false_no_update_needed(capsys, mocker):
    zippath = "/etc/openvpn/client/nordvpn/ovpn.zip"

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
