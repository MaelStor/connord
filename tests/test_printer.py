# pylint: disable=redefined-outer-name, unused-argument, unused-import, import-error

from main_test_module import get_stub


# pylint: disable=unused-variable
def test_borg_nature_of_printer():
    def init_printer():
        from connord.printer import Printer

        Printer(verbose=True, quiet=True)

    def test_printer():
        from connord.printer import Printer

        printer = Printer()
        assert printer.verbose
        assert printer.quiet


def test_print_map_good(capsys):
    from connord.printer import Printer

    printer = Printer()
    printer.print_map("50.116667", "8.683333")

    captured = capsys.readouterr()

    map_frankfurt = get_stub("de_frankfurt.map")
    assert captured.out == map_frankfurt


def test_print_map_location_does_not_exist(capsys):
    from connord.printer import Printer

    printer = Printer()

    printer.print_map("0", "0")

    captured = capsys.readouterr()
    assert not captured.out
    assert not captured.err
