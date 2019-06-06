#!/usr/bin/env python

from connord import version
from connord import __version__


def test_print_version(capsys):
    expected_version = """connord {}
connord  Copyright (C) 2019  Mael Stor <maelstor@posteo.de>
This program comes with ABSOLUTELY NO WARRANTY; This is free software, and you
are welcome to redistribute it under certain conditions; See the LICENSE file
shipped with this software for details.
""".format(
        __version__
    )

    version.print_version()
    captured_output = capsys.readouterr()
    actual_version = captured_output.out

    assert actual_version == expected_version
    assert captured_output.err == str()
