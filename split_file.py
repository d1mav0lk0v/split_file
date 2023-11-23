"""Split one file into several files given command line arguments."""


import os
import sys
import argparse
import time
import threading

from itertools import count


RED     = "\033[31m"
GREEN   = "\033[32m"
BLUE    = "\033[34m"
YELLOW  = "\033[33m"
RESET   = "\033[0m"


def error(message):
    """Show an error message and exit the program."""

    print(RED + "error: {}".format(message) + RESET)
    sys.exit(1)


def positive_int(value):
    """Validate a string for positive number value and returns that number."""

    try:
        value = int(value)
        if value <= 0:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(
            "not a positive integer: {}".format(value)
        )

    return value


def parse_command_args():
    """Run the command line arguments parser."""

    description = """description:
    {0}Split one file into several files given command line arguments.
    {0}New files are created with a sequence number suffix.
    {0}New files are not created if there are no lines to create them.
    {1}Warning: new files may erase old files!{2}""".format(GREEN, YELLOW, RESET)

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.error = error

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-l", "--nlines",
        type=positive_int,
        help="number of lines in output files",
    )

    group.add_argument(
        "-f", "--nfiles",
        type=positive_int,
        help="number of output files",
    )

    parser.add_argument(
        "-e", "--encoding",
        help="encoding of source file and output files"
    )

    parser.add_argument(
        "-t", "--title",
        action="store_true",
        help="include title (first line of the source file) in output files",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="display created output files",
    )

    parser.add_argument(
        "source_file",
        help="file name or full path file",
    )

    parser.add_argument(
        "target_dir",
        nargs="?",
        default=None,
        help="directory of output files (default: dir source_file)",
    )

    return parser.parse_args()


class Spinner:
    @staticmethod
    def spinning_cursor():
        while True:
            for cursor in "|/-\\":
                yield cursor


    def __init__(self, msg = "", delay = 0):
        self.spinner_generator = self.spinning_cursor()
        self.msg = msg
        self.delay = delay


    def spinner_task(self):
        while self.busy:
            s = next(self.spinner_generator)
            sys.stdout.write(f"{GREEN}\r{self.msg} {s} {RESET}")
            sys.stdout.flush()
            time.sleep(self.delay)
        sys.stdout.write(f"\r{' ' * (len(self.msg) + 5)}\r")
        sys.stdout.flush()


    def __enter__(self):
        self.busy = True
        self.thread = threading.Thread(target=self.spinner_task)
        self.thread.start()


    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        self.thread.join()
        if exception is not None:
            return False


def get_target_file_format(source_name, target_dir=None):
    """Return the format string in the file suffix.
    The string is the path to the file."""

    path, file = os.path.split(source_name)
    name, ext = os.path.splitext(file)
    if target_dir is not None:
        path = target_dir

    return os.path.join(path, name + "_{}" + ext)


def del_newline_endfile(file_name):
    """Remove new line at end of file."""

    with open(file_name, "rb+") as file:
        file.seek(0, 2)
        size = max(0, file.tell() - 2)

        file.seek(size, 0)
        end = file.read()

        size_diff = len(end) - len(end.rstrip())
        if size_diff != 0:
            file.truncate(file.tell() - size_diff)


def split_file_nlines(source_name, nlines, target_dir=None,
                      encoding=None, title=False, verbose=False):
    """Split source file by number of lines.

    The number of lines in the new files is the same, maybe except for the
    last one. If the total number of lines is not a multiple of the given
    number, then the last file will have fewer lines.

    The file is created if there is at least one line. Empty files are
    not created.
    """

    target_name_format = get_target_file_format(source_name, target_dir)

    with open(source_name, mode="r", encoding=encoding) as source:
        source.seek(0, 2)
        source_size = source.tell()
        source.seek(0, 0)

        title_line = source.readline() if title else ""

        for i in count(1):
            if source_size == source.tell():
                break

            target_name = target_name_format.format(i)
            if verbose:
                print(BLUE + target_name + RESET)

            with (open(target_name, mode="w+", encoding=encoding) as target,
                  Spinner("read & write:", 0.1)):
                target.write(title_line)

                for _ in range(nlines):
                    line = source.readline()
                    target.write(line)
                    if not line:
                        break

            del_newline_endfile(target_name)


def split_file_nfiles(source_name, nfiles, target_dir=None,
                      encoding=None, title=False, verbose=False):
    """Split source file by number of files.

    The resulting files contain approximately the same number of lines.

    The biggest difference is one line.

    The file is created if there is at least one line. Empty files are
    not created.
    """

    target_name_format = get_target_file_format(source_name, target_dir)

    with open(source_name, mode="r", encoding=encoding) as source:
        source.seek(0, 2)
        source_size = source.tell()
        source.seek(0, 0)

        # O(n)
        with Spinner("count lines:", 0.1):
            source_nlines = (-1 if title else 0) + sum(1 for _ in source)
            source.seek(0, 0)

        quot_source_nlines, rest_source_nlines = divmod(source_nlines, nfiles)

        title_line = source.readline() if title else ""

        for i in range(1, nfiles + 1):
            if source_size == source.tell():
                break

            target_name = target_name_format.format(i)
            if verbose:
                print(BLUE + target_name + RESET)

            nlines = quot_source_nlines
            if i <= rest_source_nlines:
                nlines += 1

            with (open(target_name, mode="w", encoding=encoding) as target,
                  Spinner("read & write:", 0.1)):
                target.write(title_line)

                for _ in range(nlines):
                    line = source.readline()
                    target.write(line)

            del_newline_endfile(target_name)


def main():
    """Run functions: parser command args and split file."""

    args = parse_command_args()

    print(GREEN + "start..."  + RESET)

    try:
        if args.nlines is not None:
            split_file_nlines(
                args.source_file,
                args.nlines,
                args.target_dir,
                args.encoding,
                args.title,
                args.verbose,
            )
        elif args.nfiles is not None:
            split_file_nfiles(
                args.source_file,
                args.nfiles,
                args.target_dir,
                args.encoding,
                args.title,
                args.verbose,
            )
    except Exception as exc:
        error(exc)
    else:
        print(GREEN + "success!"  + RESET)


if __name__ == "__main__":
    main()
