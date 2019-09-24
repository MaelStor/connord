import pytest

def test_borg_nature_of_printer():
    def init_printer():
        from connord.printer import Printer
        pr = Printer(verbose=True, quiet=True)

    def test_printer():
        from connord.printer import Printer
        pr = Printer()
        assert pr.verbose
        assert pr.quiet

def test_printer_does_not_change_initial_values
