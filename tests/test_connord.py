#!/usr/bin/env python

from connord import connord
from tests.main_test_module import get_stub, MockBase


def test_main_when_sys_argv_has_no_arguments(capsys, mocker):
    argv = ["connord"]
    help_stub = get_stub("help_message_stub.txt")

    mocker.patch.object(connord.sys, "argv", argv)

    try:
        connord.main()
        assert False
    except SystemExit:
        assert True

    captured = capsys.readouterr()
    assert captured.out == help_stub
    assert captured.err == ""


def test_main_when_command_is_update(mocker):
    argv = ["connord", "update"]
    mocker.patch.object(connord.sys, "argv", argv)

    mocked_update = mocker.patch("connord.connord.update")
    mocked_update.update.return_value = True
    mocked_update.update.side_effect = PermissionError("testing")

    try:
        connord.main()
        assert False
    except SystemExit as error:
        assert error.code == 1


def test_main_when_command_is_version(mocker):
    argv = ["connord", "version"]
    mocker.patch.object(connord.sys, "argv", argv)

    mocked_version = mocker.patch("connord.connord.version")
    mocked_version.print_version.return_value = True

    try:
        connord.main()
        assert False
    except SystemExit as error:
        assert error.code == 0


def test_main_when_command_is_list(mocker):
    argv = ["connord", "list"]
    mocker.patch.object(connord.sys, "argv", argv)

    mocked_list = mocker.patch("connord.connord.listings")
    mocked_list.list_servers.return_value = True

    try:
        connord.main()
        assert False
    except SystemExit as error:
        assert error.code == 0

    mocked_list.list_servers.assert_called_once()


def test_main_when_command_is_kill_user_is_not_root(mocker):
    argv = ["connord", "kill"]
    mocker.patch.object(connord.sys, "argv", argv)

    try:
        connord.main()
        assert False
    except SystemExit as error:
        assert error.code == 1


class ArgumentFixture:
    def __init__(
        self,
        country=None,
        area=None,
        category_=None,
        feature=None,
        netflix=None,
        iptables=None,
        top=None,
        list_sub=None,
        v4=None,
        v6=None,
        all_=None,
        table=None,
    ):
        self.country = country
        self.area = area
        self.category = category_
        self.feature = feature
        self.netflix = netflix
        self.top = top
        self.list_sub = list_sub
        self.v4 = v4
        self.v6 = v6
        self.all = all_
        self.table = table

    def set_max_load(self, load):
        self.max_load = load

    def set_min_load(self, load):
        self.min_load = load

    def set_load(self, load):
        self.load = load


def test_process_list_cmd_when_iptables_is_given(mocker):
    args = ArgumentFixture(list_sub="iptables")
    mockbase = MockBase("connord")
    mockbase.mock_user_is_root(mocker, True)
    mockbase.setup(connord)

    mocked_listings = mocker.patch("connord.connord.listings")
    mocked_listings.list_iptables.return_value = True

    connord.process_list_cmd(args)

    mocked_listings.list_iptables.assert_called_once_with(["filter"], "4")


def test_process_list_servers_cmd_when_max_load_is_given(mocker):
    args = ArgumentFixture()
    args.set_max_load(10)
    args.set_min_load(None)
    args.set_load(None)

    mocked_list = mocker.patch("connord.connord.listings")
    mocked_list.list_servers.return_value = True

    connord.process_list_servers_cmd(args)

    mocked_list.list_servers.assert_called_once_with(
        None, None, None, None, None, 10, "max", None
    )


def test_process_list_servers_cmd_when_min_load_is_given(mocker):
    args = ArgumentFixture()
    args.set_max_load(None)
    args.set_min_load(10)
    args.set_load(None)

    mocked_list = mocker.patch("connord.connord.listings")
    mocked_list.list_servers.return_value = True

    connord.process_list_servers_cmd(args)

    mocked_list.list_servers.assert_called_once_with(
        None, None, None, None, None, 10, "min", None
    )


def test_process_list_servers_cmd_when_load_is_given(mocker):
    args = ArgumentFixture()
    args.set_max_load(None)
    args.set_min_load(None)
    args.set_load(10)

    mocked_list = mocker.patch("connord.connord.listings")
    mocked_list.list_servers.return_value = True

    connord.process_list_servers_cmd(args)

    mocked_list.list_servers.assert_called_once_with(
        None, None, None, None, None, 10, "exact", None
    )


def test_process_list_servers_cmd_when_load_is_default(mocker):
    args = ArgumentFixture()
    args.set_max_load(None)
    args.set_min_load(None)
    args.set_load(None)

    mocked_list = mocker.patch("connord.connord.listings")
    mocked_list.list_servers.return_value = True

    connord.process_list_servers_cmd(args)

    mocked_list.list_servers.assert_called_once_with(
        None, None, None, None, None, 100, "max", None
    )


def test_main_provoking_not_implemented_error(mocker):
    # The exception shouldn't happen under normal circumstances.
    # This test just covers the last statement to get 100% coverage.
    mocked_sys = mocker.patch("connord.connord.sys")
    mocked_sys.argv.return_value = ["connord"]

    try:
        connord.main()
        assert False
    except NotImplementedError as error:
        assert str(error) == "Could not process command-line arguments."
