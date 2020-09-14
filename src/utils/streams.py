#!/usr/bin/env python3

import sys
from typing import NoReturn


def print_err(*args, **kwargs):
    print(args, file=sys.stderr, **kwargs)


# from https://stackoverflow.com/a/27871113
def progress(count, total, suffix='') -> NoReturn:
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    if count == total:
        string = '[%s] %s%s%s \n' % (bar, 100, '%', " " * 30)
    else:
        string = '[%s] %s%s ... %s%s\r' % (bar, percents, '%', suffix, " " * 20)

    sys.stdout.write(string)
    sys.stdout.flush()
