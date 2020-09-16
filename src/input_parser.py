#!/usr/bin/env python3

import argparse
import re
from typing import List, Dict, Any
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
    operation_parser.add_argument('-wd', '--working_directory', type=str, help='The working directory.', required=True)
    operation_parser.add_argument('-pf', '--prefix', type=str, default=None,
                                  help='Path prefix for extra compile and test files for the unknown arguments')
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


def run(base: Base, **kwargs):
    try:
        if "regex" in kwargs:
            kwargs = parse_unknown(**kwargs)
        base = base(**kwargs)
        base()
    except Exception as e:
        with open("exception.log", "a") as ex:
            ex.write(str(e) + "\n")
            print(e)


import tasks.catalog
import tasks.check
import tasks.genpolls
import operations.info
import operations.compile
import operations.checkout
import operations.test
