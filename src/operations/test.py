#!/usr/bin/env python3

import psutil
from os import listdir
from pathlib import Path
from typing import List, AnyStr

from context import Context
from utils.parse import parse_results, kill_process
from utils.coverage import Coverage
from input_parser import add_operation


class Test(Context):
    def __init__(self,
                 tests: List[AnyStr] = None, out_file: str = None, port: str = None, pos_tests: bool = False,
                 neg_tests: bool = False, exit_fail: bool = False, write_fail: bool = False, neg_pov: bool = True,
                 cov_dir: str = None, cov_out_dir: str = None, cov_suffix: str = ".path", rename_suffix: str = ".path",
                 **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.port = port
        self.neg_pov = neg_pov
        self.exit_fail = exit_fail
        self.write_fail = write_fail
        self.out_file = Path(out_file) if out_file else out_file
        self.coverage = Coverage(cov_dir if cov_dir else self.cmake, cov_out_dir, cov_suffix, rename_suffix)
        self.challenge.load_pos_tests()
        self.challenge.load_neg_tests(self.build)

        if tests:
            self.tests = tests
        elif pos_tests:
            if not self._load_checks("pos_checks.txt"):
                self.tests = self.challenge.pos_tests.keys()
        elif neg_tests:
            if not self._load_checks("neg_checks.txt"):
                self.tests = self.challenge.neg_tests.keys()
        else:
            if not self._load_checks("checks.txt"):
                self.tests = list(self.challenge.pos_tests.keys()) + list(self.challenge.neg_tests.keys())

        self.log(str(self))

    def __call__(self, save: bool = False):
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
                                        exit_err=False)
            if err:
                print(err)

            self.coverage()
            total, passed = parse_results(out)
            if passed == '2':
                self._kill_error_process()
            # Negative tests should fail
            if self.is_pov and self.neg_pov:
                if passed == '1':
                    passed = '0'
                else:
                    passed = '1'

            tests_result[test] = passed

            if passed != '1':
                if not self.write_fail:
                    tests_result.pop(test)

                if self.exit_fail:
                    failed = True
                    break

        if self.out_file is not None:
            self.write_results(tests_result)

        if save:
            return tests_result

        if failed:
            exit(1)
        exit(0)

    def _cmd_str(self):
        # Collect the names of binaries to be tested
        cb_dirs = [el for el in listdir(str(self.source)) if el.startswith('cb_')]

        if len(cb_dirs) > 0:
            # There are multiple binaries in this challenge
            bin_names = ['{}_{}'.format(self.challenge.name, i + 1) for i in range(len(cb_dirs))]
        else:
            bin_names = [self.challenge.name]

        cb_cmd = [str(self.get_tools().test),
                  '--directory', str(self.build),
                  '--xml', str(self.test_file),
                  '--concurrent', '4',
                  '--debug',
                  '--timeout', self.configuration.tests_timeout,
                  '--negotiate_seed', '--cb'] + bin_names

        if self.port is not None:
            cb_cmd += ['--port', self.port]

        if self.is_pov:
            cb_cmd += ['--should_core']

        return cb_cmd

    def write_results(self, results: dict):
        out_file = self.add_prefix(self.out_file)

        if not out_file.is_dir():
            with out_file.open(mode="a") as of:
                for k, v in results.items():
                    of.write(f"{k} {v}\n")

    def _load_checks(self, file_name: str) -> bool:
        path_tests = self.source / Path(file_name)

        if path_tests.exists():
            with path_tests.open(mode="r") as t:
                self.tests = t.read().split()

            if not self.tests:
                self.status(f"No checked tests.\n")
                return False

            self.status(f"Loaded checked tests {' '.join(self.tests)}.\n")
            return True

        return False

    def _kill_error_process(self):
        """
        Get a list of all the PIDs of a all the running process whose name contains
        the given string processName and kill the process
        """
        # based on https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
        # Iterate over the all the running process

        for proc in psutil.process_iter():
            try:
                proc_info = proc.as_dict(attrs=['pid', 'name', 'create_time'])
                # Check if process name contains the given name string.
                if self.challenge.name in proc_info['name']:
                    self.status(f"Killing {self.challenge.name} process with pid {proc_info['pid']}.\n")
                    kill_process(proc_info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

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
    # Coverage group
    g = input_parser.add_argument_group(title="coverage", description="None")
    g.add_argument('-cd', '--cov_dir', type=str, help='The dir where the coverage files are generated.', default=None)
    g.add_argument('-cod', '--cov_out_dir', type=str, help='The dir where the coverage files are output.', default=None)
    g.add_argument('-cs', '--cov_suffix', type=str, help='The suffix of the coverage files generated.', default=".path")
    g.add_argument('-rs', '--rename_suffix', type=str, default=".path",
                   help='Rename the suffix to a specific one when outputting files')

    input_parser.add_argument('-of', '--out_file', type=str, help='The file where tests results are written to.')
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
