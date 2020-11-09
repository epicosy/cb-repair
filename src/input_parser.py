#!/usr/bin/env python3

import argparse
import re
from typing import List, Dict, Any
from core.kernel import Kernel
from core.task import Task
from core.operation import Operation
from core.simple_operation import SimpleOperation

parser = argparse.ArgumentParser(prog="cb-repair",
                                 description='CGC Benchmark plugin for automatic program repair tools.')
challenge_parser = argparse.ArgumentParser(add_help=False)

challenge_parser.add_argument('-v', '--verbose', help='Verbose output.', action='store_true')
challenge_parser.add_argument('--excl', help='Flag for not skipping excluded challenges.', action='store_true')
challenge_parser.add_argument('-l', '--log_file', type=str, default=None,
                              help='Log file to write the results to.')

subparsers = parser.add_subparsers()


def add_operation(name: str, operation: Operation, description: str):
    operation_parser = add_simple_operation(name, operation, description)
    operation_parser.add_argument('-wd', '--working_directory', type=str, help='The working directory.', required=True)
    operation_parser.add_argument('-pf', '--prefix', type=str, default=None,
                                  help='Path prefix for extra compile and test files for the unknown arguments')
    operation_parser.add_argument('-r', '--regex', type=str, default=None,
                                  help='File containing the regular expression to parse unknown arguments into known')

    return operation_parser


def add_simple_operation(name: str, simple_operation: SimpleOperation, description: str):
    simple_operation_parser = add_kernel(name, simple_operation, description)
    simple_operation_parser.add_argument('-cn', '--challenge', type=str, help='The challenge name.', required=True)

    return simple_operation_parser


def add_task(name: str, task: Task, description: str):
    task_parser = add_kernel(name, task, description)
    task_parser.add_argument('--challenges', type=str, nargs='+', required=False, help='The challenges to be checked.')

    return task_parser


def add_kernel(name: str, kernel: Kernel, description: str):
    kernel_parser = subparsers.add_parser(name=name, help=description, parents=[challenge_parser])
    kernel_parser.set_defaults(kernel=kernel)
    kernel_parser.set_defaults(name=name)

    return kernel_parser


def parse_unknown(regex: str, unknown: List[str], **kwargs) -> Dict[str, Any]:
    if regex and unknown:
        args_matches = {}

        with open(regex, "r") as f:
            exp = f.readline()
            exp = exp.splitlines()[0]

            for arg in unknown:
                match = re.match(exp, arg)

                if match:
                    for key, value in match.groupdict().items():
                        if key in args_matches:
                            if isinstance(args_matches[key], list):
                                args_matches[key].append(value)
                            else:
                                args_matches[key] = [args_matches[key], value]
                        else:
                            args_matches[key] = value

            kwargs.update(args_matches)
            return kwargs

    return kwargs


def run(kernel: Kernel, **kwargs):
    if "regex" in kwargs:
        kwargs = parse_unknown(**kwargs)
    kernel = kernel(**kwargs)
    kernel()


import tasks.catalog
import tasks.check
import tasks.score
import tasks.clean
import operations.info
import operations.compile
import operations.checkout
import operations.simple.genpolls
import operations.simple.manifest
import operations.simple.patch
import operations.test
