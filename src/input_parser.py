#!/usr/bin/env python3

import argparse
import re
from typing import List
from base import Base

parser = argparse.ArgumentParser(prog="cb-repair",
                                 description='CGC Benchmark plugin for automatic program repair tools.')
challenge_parser = argparse.ArgumentParser(add_help=False)

challenge_parser.add_argument('-v', '--verbose', help='Verbose output.', action='store_true')
challenge_parser.add_argument('-l', '--log_file', type=str, default=None,
                              help='Log file to write the results to.')

subparsers = parser.add_subparsers()


def add_operation(name: str, operation: Base, description: str):
    operation_parser = add_task(name, operation, description)
    operation_parser.add_argument('-wd', '--working_directory', type=str, help='The working directory.')
    operation_parser.add_argument('-pf', '--prefix', type=str, default=None,
                                  help='Path prefix for extra compile and test files from the unknown arguments')
    operation_parser.add_argument('-r', '--regex', type=str, default=None,
                                  help='File containing the regular expression to parse unknown arguments into known')

    return operation_parser


def add_task(name: str, task: Base, description: str):
    task_parser = add_base(name, task, description)
    task_parser.add_argument('-cn', '--challenge_name', type=str, help='The challenge name.', required=True)

    return task_parser


def add_base(name: str, base: Base, description: str):
    base_parser = subparsers.add_parser(name=name, help=description, parents=[challenge_parser])
    base_parser.set_defaults(base=base)
    base_parser.set_defaults(name=name)

    return base_parser


def parse_unknown(regex: str, unknown: List[str]) -> dict:
    if regex and unknown:
        unk_str = ' '.join(unknown)

        with open(regex, "r") as f:
            exp = f.readline()
            exp = exp.split("\n")[0]
            match = re.match(exp, unk_str)

        if match:
            return match.groupdict()

    return dict()


def run(base: Base, **kwargs):
    if "regex" in kwargs:
        parsed_unk = parse_unknown(kwargs["regex"], **kwargs)
        kwargs.update(parsed_unk)

    base = base(**kwargs)
    base()


import tasks.catalog
import tasks.genpolls
import operations.info
import operations.compile
import operations.checkout
import operations.test
