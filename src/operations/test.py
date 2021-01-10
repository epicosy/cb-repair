#!/usr/bin/env python3
import os
import binascii
import time

from os import listdir
from pathlib import Path
from typing import List, AnyStr

from core.operation import Operation
from utils.test_result import TestResult
from utils.process_manager import ProcessManager
from input_parser import add_operation


class Test(Operation):
    def __init__(self,
                 tests: List[AnyStr] = None, out_file: str = None, port: str = None, pos_tests: bool = False,
                 neg_tests: bool = False, exit_fail: bool = False, write_fail: bool = False, neg_pov: bool = True,
                 timeout: int = None, print_ids: bool = False, print_class: bool = False, only_numbers: bool = False,
                 cores_path: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.port = port
        self.neg_pov = neg_pov
        self.exit_fail = exit_fail
        self.write_fail = write_fail
        self.print_ids = print_ids
        self.print_class = print_class
        self.only_numbers = only_numbers
        self.out_file = Path(out_file) if out_file else out_file
        self.test_timeout = timeout if timeout else int(self.configs.tests_timeout)
        self.challenge.load_pos_tests()
        self.challenge.load_neg_tests(self.build)
        self.stats = self.working_dir / Path("stats", "tests.txt")
        self.stats.parent.mkdir(parents=True, exist_ok=True)
        self.cores_path = cores_path
        self.process_manager = ProcessManager(process_name=self.challenge.name)
        self.results = {}

        if tests:
            self.tests = self.map_only_number_ids(tests) if self.only_numbers else tests
        elif pos_tests:
            self.tests = self.challenge.pos_tests.keys()
        elif neg_tests:
            self.tests = self.challenge.neg_tests.keys()
        else:
            self.tests = list(self.challenge.pos_tests.keys()) + list(self.challenge.neg_tests.keys())

        self.log(str(self))

    def __call__(self, save: bool = False):
        self.status(f"Running {len(self.tests)} tests.")

        for test in self.tests:
            self._set_test(test)
            start = time.time()
            self._run_test()
            end = time.time()
            difference = int(end - start)
            self._process_result(duration=difference)
            self._process_flags()

        if save:
            return self.results
        exit(0)

    def map_only_number_ids(self, ids: List[AnyStr]):
        pos_tests = {int(t_id.replace('p', '')): t_id for t_id in self.challenge.pos_tests.keys()}
        count_pos_tests = len(pos_tests)
        neg_tests = {int(t_id.replace('n', '')) + count_pos_tests: t_id for t_id in self.challenge.neg_tests.keys()}
        tests = []

        for test in ids:
            int_test = int(test)
            if int_test not in pos_tests and int_test not in neg_tests:
                self.status(f"Test {test} could not be mapped with available tests.", err=True)
            else:
                tests.append(pos_tests[int_test] if int_test in pos_tests else neg_tests[int_test])

        if not tests:
            self.status(f"Input tests could not be mapped with available tests.", err=True)

        return tests

    def _set_test(self, test: str):
        try:
            self.current_test = test
            self.test_file, self.is_pov = self.challenge.get_test(test)
        except Exception as e:
            self.error = str(e)
            self.status(self.error, err=True)
            exit(1)

    def _run_test(self):
        super().__call__(cmd_str=self._cmd_str(), cmd_cwd=str(self.get_tools().root), timeout=self.test_timeout,
                         msg=f"Testing {self.challenge.name} on {self.test_file.name}\n", exit_err=False)
        if self.error:
            self.status(self.error, err=True)

    def _process_result(self, total: int = 1, duration: int = 0):
        self.results[self.current_test] = TestResult(self.output, total, self.is_pov, duration)
        error = self.results[self.current_test].error

        if error:
            self.status(error, err=True)
            self.status(f"Killing {self.challenge.name} process.", bold=True)
            self.process_manager.kill(pids=self.results[self.current_test].pids)
            self.status(f"Killed processes {self.process_manager.pids}.", bold=True)

        self.outcome()

    def _process_flags(self):
        if self.is_pov and self.neg_pov:
            # Invert negative test's result
            self.results[self.current_test].passed ^= 1

        if self.print_ids and self.results[self.current_test].passed:
            if self.only_numbers:
                print(self.current_test[1:])
            else:
                print(self.current_test)
        if self.print_class:
            print("PASS" if self.results[self.current_test].passed else 'FAIL')

        if self.out_file is not None:
            self.write_result()

        if self.exit_fail and not self.results[self.current_test].passed:
            exit(1)

    def _cmd_str(self):
        # Collect the names of binaries to be tested
        cb_dirs = [el for el in listdir(str(self.source)) if el.startswith('cb_')]

        if len(cb_dirs) > 0:
            # There are multiple binaries in this challenge
            bin_names = ['{}_{}'.format(self.challenge.name, i + 1) for i in range(len(cb_dirs))]
        else:
            bin_names = [self.challenge.name]
        duration = self.get_test_duration()
        # use timeout or duration from sanity check
        timeout = str(self.test_timeout) if duration is None else str(duration + self.configs.margin)
        cb_cmd = [str(self.get_tools().test), '--directory', str(self.build), '--xml', str(self.test_file),
                  '--concurrent', '1', '--debug', '--timeout', timeout, '--negotiate_seed',
                  '--cb'] + bin_names

        if self.port is not None:
            cb_cmd += ['--port', self.port]

        if self.is_pov:
            if self.cores_path:
                cb_cmd += ['--cores_path']
            cb_cmd += ['--should_core']
            # double check
            cb_cmd += ['--pov_seed', binascii.b2a_hex(os.urandom(48))]

        return cb_cmd

    def get_test_duration(self):
        if self.current_test in self.global_metadata[self.challenge.name]["durations"]:
            return self.global_metadata[self.challenge.name]["durations"][self.current_test]
        return None

    def write_result(self):
        out_file = self.add_prefix(self.out_file)
        if not self.write_fail and not self.results[self.current_test].passed:
            return
        with out_file.open(mode="a") as of:
            of.write(f"{self.current_test} {self.results[self.current_test].passed}\n")

    def outcome(self):
        with self.stats.open(mode="a") as s, (self.stats.parent / "track.txt").open(mode="r") as tf:
            cid = tf.read().split()[0]
            s.write(f"{self.current_test} {self.results[self.current_test].passed} {self.results[self.current_test].code} {cid}\n")

    def __str__(self):
        test_cmd_str = " --tests " + ' '.join(self.tests)

        if self.port:
            test_cmd_str += f" --port {self.port}"

        if self.out_file:
            test_cmd_str += f" --out_file {self.out_file}"

        return super().__str__() + test_cmd_str + "\n"


def test_args(input_parser):
    # Tests group
    g = input_parser.add_mutually_exclusive_group(required=False)
    g.add_argument('-pt', '--pos_tests', action='store_true', required=False,
                   help='Run all positive tests against the challenge.')
    g.add_argument('-nt', '--neg_tests', action='store_true', required=False,
                   help='Run all negative tests against the challenge.')
    g.add_argument('-tn', '--tests', type=str, nargs='+', help='Name of the test', required=False)

    # Print group
    p = input_parser.add_mutually_exclusive_group(required=False)
    p.add_argument('-PI', '--print_ids', action='store_true', help='Flag for printing the list of passed testcase ids.')
    p.add_argument('-P', '--print_class', action='store_true', help='Flag for printing testcases outcome as PASS/FAIL.')

    input_parser.add_argument('-of', '--out_file', type=str, help='The file where tests results are written to.')
    input_parser.add_argument('--cores_path', action='store_true',
                              help='Enables for Linux core storage under the /cores path.')
    input_parser.add_argument('-on', '--only_numbers', action='store_true',
                              help='Testcase ids are only numbers. Negative tests are counter after the positive.')
    input_parser.add_argument('-T', '--timeout', type=int, help='Timeout for the tests.', required=False)
    input_parser.add_argument('-wf', '--write_fail', action='store_true',
                              help='Flag for writing the failed test to the specified out_file.')
    input_parser.add_argument('-np', '--neg_pov', action='store_true',
                              help='Flag for reversing the passed result if is a negative test.')
    input_parser.add_argument('-ef', '--exit_fail', action='store_true',
                              help='Flag that makes program exit with error when a test fails.')
    input_parser.add_argument('-pn', '--port', type=str, default=None,
                              help='The TCP port used for testing the CB. \
                               If PORT is not provided, a random port will be used.')


t_parser = add_operation("test", Test, 'Runs specified tests against challenge binary.')
test_args(t_parser)
