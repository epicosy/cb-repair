#!/usr/bin/env python3

import argparse
import re
from typing import List, Union
from operation import Operation
from setting import Setting

parser = argparse.ArgumentParser(prog="cb-repair",
                                 description='CGC Benchmark plugin for automatic program repair tools.')
challenge_parser = argparse.ArgumentParser(add_help=False)
challenge_parser.add_argument('-cn', '--challenge_name', type=str, help='The challenge name.')
challenge_parser.add_argument('-v', '--verbose', help='Verbose output.', action='store_true')
challenge_parser.add_argument('-l', '--log_file', type=str, default=None,
                              help='Log file to write the results to.')

subparsers = parser.add_subparsers()


def add_operation(name: str, operation: Operation, description: str):
    operation_parser = subparsers.add_parser(name=name, help=description, parents=[challenge_parser])
    operation_parser.add_argument('-wd', '--working_directory', type=str, help='The working directory.')
    operation_parser.add_argument('-pf', '--prefix', type=str, default=None,
                                  help='Path prefix for extra compile and test files from the unknown arguments')
    operation_parser.add_argument('-r', '--regex', type=str, default=None,
                                  help='File containing the regular expression to parse unknown arguments into known')
    operation_parser.set_defaults(setting=operation)
    operation_parser.set_defaults(name=name)

    return operation_parser


def add_task(name: str, task: Setting, description: str):
    task_parser = subparsers.add_parser(name=name, help=description, parents=[challenge_parser])
    task_parser.set_defaults(setting=task)
    task_parser.set_defaults(name=name)

    return task_parser


def parse_unknown(regex: str, unknown: str) -> dict:
    with open(regex, "r") as f:
        exp = f.readline()
        exp = exp.split("\n")[0]
        match = re.match(exp, unknown)

    if match:
        return match.groupdict()

    return dict()


def run(unknown: List[str], setting: Union[Operation, Setting], **kwargs):
    if "regex" in kwargs and unknown:
        unk_args = ' '.join(unknown)
        parsed_unk = parse_unknown(kwargs["regex"], unk_args)
        kwargs.pop("regex")
        kwargs.update(parsed_unk)

    setting = setting(**kwargs)
    setting()


import tasks.info
import tasks.genpolls
import operations.compile
import operations.checkout
import operations.test
