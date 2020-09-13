#!/usr/bin/env python3

from os import listdir
from pathlib import Path
from typing import List

from context import Context
from utils.parse import parse_results
from input_parser import add_operation


class Test(Context):
    def __init__(self,
                 tests: List[str],
                 out_file: str,
                 port: str,
                 pos_tests: bool,
                 neg_tests: bool,
                 exit_fail: bool,
                 write_fail: bool,
                 **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.port = port
        self.exit_fail = exit_fail
        self.write_fail = write_fail
        self.out_file = Path(out_file) if out_file is not None else out_file
        self.challenge.load_pos_tests()
        self.challenge.load_neg_tests(self.build)

        if tests:
            self.tests = tests
        elif pos_tests:
            self.tests = self.challenge.pos_tests.keys()
        elif neg_tests:
            self.tests = self.challenge.neg_tests.keys()
        else:
            self.tests = list(self.challenge.pos_tests.keys()) + list(self.challenge.neg_tests.keys())

        self.log(str(self))

    def __call__(self):
        failed = False
        tests_result = {}
        # TODO: Change this, cb-test.py accepts more challenges at once,
        #       might influence how results are processed
        self.status(f"Running {len(self.tests)} tests.\n")

        for test in self.tests:
            self.test_file, self.is_pov = self.challenge.get_test(test)

            out, err = super().__call__(cmd_str=self._cmd_str(),
                                        msg=f"Testing {self.challenge.name} on {self.test_file.name}\n",
                                        cmd_cwd=str(self.get_tools().root),
                                        timeout=int(self.configuration.tests_timeout),
                                        exit_err=True)

            total, passed = parse_results(out, self.is_pov)
            tests_result[test] = passed

            if passed == '0':
                if not self.write_fail:
                    tests_result.pop(test)

                if self.exit_fail:
                    failed = True
                    break

        if self.out_file is not None:
            self.write_results(tests_result)

        if failed:
            exit(1)
        exit(0)

    def _cmd_str(self):
        # Collect the names of binaries to be tested
        cb_dirs = [el for el in listdir(str(self.build)) if el.startswith('cb_')]

        if len(cb_dirs) > 0:
            # There are multiple binaries in this challenge
            bin_names = ['{}_{}'.format(self.challenge.name, i + 1) for i in range(len(cb_dirs))]
        else:
            bin_names = [self.challenge.name]

        cb_cmd = [str(self.get_tools().test),
                  '--directory', str(self.build),
                  '--xml', str(self.test_file),
                  '--concurrent', '4',
                  '--timeout', self.configuration.tests_timeout,
                  '--negotiate_seed', '--cb'] + bin_names

        if self.port is not None:
            cb_cmd += ['--port', self.port]

        if self.is_pov:
            cb_cmd += ['--should_core']

        return cb_cmd

    def write_results(self, results: dict):
        out_file = self.add_prefix(self.out_file)

        with out_file.open(mode="a") as of:
            for k, v in results.items():
                of.write(f"{k} {v}\n")

    def __str__(self):
        test_cmd_str = " --tests " + ' '.join(self.tests)

        if self.port:
            test_cmd_str += f" --port {self.port}"

        if self.out_file:
            test_cmd_str += f" --out_file {self.out_file}"

        return super().__str__() + test_cmd_str + "\n"


def test_args(input_parser):
    g = input_parser.add_mutually_exclusive_group(required=False)
    g.add_argument('-pt', '--pos_tests', action='store_true', required=False,
                   help='Run all positive tests against the challenge.')
    g.add_argument('-nt', '--neg_tests', action='store_true', required=False,
                   help='Run all negative tests against the challenge.')
    g.add_argument('-tn', '--tests', type=str, nargs='+', help='Name of the test', required=False)
    input_parser.add_argument('-of', '--out_file', type=str, help='The file where tests results are written to.')
    input_parser.add_argument('-wf', '--write_fail', action='store_true',
                              help='Flag for writing the failed test to the specified out_file.')
    input_parser.add_argument('-ef', '--exit_fail', action='store_true',
                              help='Flag that makes program exit with error when a test fails.')
    input_parser.add_argument('-pn', '--port', type=str, default=None,
                              help='The TCP port used for testing the CB. \
                               If PORT is not provided, a random port will be used.')


t_parser = add_operation("test", Test, 'Runs specified tests against challenge binary.')
test_args(t_parser)
