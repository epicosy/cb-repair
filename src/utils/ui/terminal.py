
import sys
from typing import NoReturn


# from https://stackoverflow.com/a/27871113
def progress(count, total, suffix='') -> NoReturn:
    count += 1
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = Colors.ok('▇' * filled_len + '-' * (bar_len - filled_len), '')

    if count == total:
        info = Colors.info(f"100% {' ' * 30}", '')
        string = f"▏{bar}▕ {info} \n"
    else:
        info = Colors.info(f"{percents}% ... {suffix}{' ' * 20}", '')
        string = f"▏{bar}▕ {info}\r"

    sys.stdout.write(string)
    sys.stdout.flush()


# source: https://stackoverflow.com/a/47622205
# Colored printing functions for strings that use universal ANSI escape sequences.
# fail: bold red, pass: bold green, warn: bold yellow,
# info: bold blue, bold: bold white
class TermPrint:

    @staticmethod
    def print_fail(message, end='\n'):
        sys.stderr.write('\x1b[1;31m' + message.strip() + '\x1b[0m' + end)

    @staticmethod
    def print_pass(message, end='\n'):
        sys.stdout.write('\x1b[1;32m' + message.strip() + '\x1b[0m' + end)

    @staticmethod
    def print_warn(message, end='\n'):
        sys.stderr.write('\x1b[1;33m' + message.strip() + '\x1b[0m' + end)

    @staticmethod
    def print_info(message, end='\n'):
        sys.stdout.write('\x1b[1;34m' + message.strip() + '\x1b[0m' + end)

    @staticmethod
    def print_bold(message, end='\n'):
        sys.stdout.write('\x1b[1;37m' + message.strip() + '\x1b[0m' + end)


class Colors:

    @staticmethod
    def fail(message, end='\n'):
        return f"\033[91m{message}\033[0m{end}"

    @staticmethod
    def ok(message, end='\n'):
        return f"\033[92m{message}\033[0m{end}"

    @staticmethod
    def warn(message, end='\n'):
        return f"\033[93m{message}\033[0m{end}"

    @staticmethod
    def info(message, end='\n'):
        return f"\033[94m{message}\033[0m{end}"

    @staticmethod
    def cyan(message, end='\n'):
        return f"\033[96m{message}\033[0m{end}"


class Format:

    @staticmethod
    def bold(message, end='\n'):
        return f"\033[1m{message}\033[0m{end}"

    @staticmethod
    def under(message, end='\n'):
        return f"\033[4m{message}\033[0m{end}"

    @staticmethod
    def head(message, end='\n'):
        return f"\033[95m{message}\033[0m{end}"
