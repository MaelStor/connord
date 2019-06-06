#!/usr/bin/env python

import os
from connord import user


def test_prompt_sudo_when_user_is_not_root(mocker):
    mocked_os = mocker.patch("connord.user.os")
    mocked_os.geteuid.return_value = 1000
    mocked_subprocess = mocker.patch("connord.user.subprocess")
    mocked_subprocess.check_call.return_value = True

    retval = user.prompt_sudo()

    mocked_os.geteuid.assert_called_once()
    mocked_subprocess.check_call.assert_called_once_with(
        "sudo -v -p '[connord][sudo] password needed: '", shell=True
    )
    assert retval


def test_prompt_sudo_when_user_is_root(mocker):
    mocked_os = mocker.patch("connord.user.os")
    mocked_os.geteuid.return_value = 0
    mocked_subprocess = mocker.patch("connord.user.subprocess")
    mocked_subprocess.check_call.return_value = True

    retval = user.prompt_sudo()

    mocked_os.geteuid.assert_called_once()
    mocked_subprocess.check_call.assert_not_called()
    assert retval


def test_is_root_when_user_is_not_root(mocker):
    mocked_os = mocker.patch("connord.user.os")
    mocked_os.geteuid.return_value = 1

    retval = user.is_root()

    mocked_os.geteuid.assert_called_once()
    assert not retval


def test_is_root_when_user_is_root(mocker):
    mocked_os = mocker.patch("connord.user.os")
    mocked_os.geteuid.return_value = 0

    retval = user.is_root()

    mocked_os.geteuid.assert_called_once()
    assert retval
