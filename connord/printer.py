import errno
import sys

from progress.bar import IncrementalBar
from progress.spinner import Spinner

from connord import sqlite


class Borg:
    """Define a borg class"""

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Printer(Borg):
    """Generic printer. Every intentional output must go through this printer
    to recognize quiet and verbose mode set on the command-line or in the
    configuration.
    """

    prefix = "connord: "

    def __init__(self, verbose=False, quiet=False):
        """Initialize the printer. The attributes don't change once they are set.

        :param verbose: if True print info messages
        :param quiet: if True suppress error and info messages
        """

        Borg.__init__(self)
        if "verbose" not in self.__dict__.keys():
            self.verbose = verbose
        if "quiet" not in self.__dict__.keys():
            self.quiet = quiet

    def yes_no(self, question):
        reply = input(question + " (y/N): ").lower().strip()
        if not reply:
            return False
        if reply in ("y", "ye", "yes"):
            return True
        if reply in ("n", "no"):
            return False

        return self.yes_no("Invalid answer. Try 'y' or 'n' or enter for No.")

    def error(self, message):
        """Prints errors if not quiet"""
        if not self.quiet:
            print(self.prefix + message, file=sys.stderr)

    def info(self, message, no_prefix=False, no_newline=False):
        """Prints info messages if verbose"""
        if self.verbose and not self.quiet:
            if no_prefix:
                message_prefixed = message
            else:
                message_prefixed = self.prefix + message
            if no_newline:
                print(message_prefixed, end="")
            else:
                print(message_prefixed)

    @staticmethod
    def write(message):
        """Prints messages independently from verbose and quiet settings
        There's no need to call this function directly. Just pass Printer to the
        file attribute of the __builtin__ print method.

        Example: print('something', file=Printer())
        """
        try:
            print(message, end="")
        except IOError as error:
            if error.errno != errno.EPIPE:
                raise

    @staticmethod
    def format_prefix(prefix):
        if len(prefix) < 40:
            return "{!s:40}".format(prefix)

        return "{!s:40} ".format(prefix)

    class Do:
        def __init__(self, message):
            self.printer = Printer()
            self.message = self.printer.format_prefix(message)

        def __enter__(self):
            self.printer.info(self.message, no_newline=True)

        # pylint: disable=redefined-builtin
        def __exit__(self, type, value, traceback):
            if type:
                self.printer.info("Error", no_prefix=True)
            else:
                self.printer.info("Done", no_prefix=True)

    def incremental_bar(self, message="", **kwargs):
        """Return an Incremental bar if verbose else a NullBar(IncrementalBar)
        which does nothing but can be used like the usual IncrementalBar

        :param message: the prefix message
        :param kwargs: kwargs to pass through to the IncrementalBar
        :returns: IncrementalBar if verbose else NullBar
        """
        if self.verbose:
            return IncrementalBar(self.format_prefix(message), bar_prefix="|", **kwargs)

        return self.NullBar()

    def spinner(self, message="", **kwargs):
        """Return a Spinner"""
        if self.verbose:
            return Spinner(self.format_prefix(message), **kwargs)

        return self.NullSpinner()

    class NullSpinner(Spinner):
        """Fake a Spinner doing nothing"""

        # pylint: disable=super-init-not-called
        def __init__(self, message="", **kwargs):
            pass

        def start(self):
            pass

        def update(self):
            pass

        def show(self, *args, **kwargs):
            pass

        def next(self, n=1):
            pass

        def write(self, s):
            pass

        def finish(self):
            pass

    class NullBar(IncrementalBar):
        """Fake an IncrementalBar doing nothing"""

        # pylint: disable=super-init-not-called
        def __init__(self, message="", **kwargs):
            pass

        def start(self):
            pass

        def update(self):
            pass

        def show(self, *args, **kwargs):
            pass

        def next(self, n=1):
            pass

        def write(self, s):
            pass

        def finish(self):
            pass

    def print_map(self, latitude, longitude):
        con = sqlite.create_connection()
        map_s = sqlite.get_map(con, latitude, longitude)

        if map_s is not None:
            print(map_s, file=self)
