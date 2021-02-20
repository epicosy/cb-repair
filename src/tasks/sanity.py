#!/usr/bin/env python3

import os
import traceback

from pathlib import Path
from typing import AnyStr, Dict

import operations.compile as compile
import operations.test as test

from core.task import Task
from input_parser import add_task
from utils.ui.tasks.check import CheckUI
from operations.simple.genpolls import GenPolls
from operations.simple.checkout import Checkout


class Sanity(Task):
    def __init__(self, timeout: int, genpolls: bool, persistent: bool, suppress_assertion: bool, count: int,
                 keep: bool = False, strict: bool = False, lookup: int = None, **kwargs):
        super().__init__(**kwargs)
        self.current = None
        self.working_dir = None
        self.genpolls = genpolls
        self.suppress_assertion = suppress_assertion
        self.persistent = persistent
        self.count = count
        self.strict = strict
        self.lookup = lookup
        self.timeout = timeout
        self.ui = CheckUI()
        self.keep = keep

    def __call__(self):
        if not self.challenges:
            self.challenges = self.get_challenges()
            self.challenges.sort()

        self.lib_paths = self.get_lib_paths()

        try:
            for challenge in self.challenges:
                self.current = challenge
                self.ui(challenge)
                self.working_dir = f"/tmp/check_{self.current}"
                self.log_file = Path(self.working_dir, "check.log")
                if self.genpolls and self.lookup:
                    self._lookup()
                else:
                    self.check()
                os.system('clear')
                self.ui.print()
        except Exception as e:
            if not self.keep:
                self.dispose()
            self.log_file = Path("check_exception.log")
            self.status(f"The follwoing exception was raised for the challenge {self.current}")
            self.status(traceback.format_exc(), err=True)

    def dispose(self):
        os.system(f"rm -rf {self.working_dir}")
        self.log_file = None
        self.status("Deleted temporary files generated", bold=True)
        # os.system('clear')

    def check(self):
        operations = [self.check_checkout, self.check_compile, self.check_test]

        if self.genpolls:
            operations.insert(0, self.check_genpolls)

        for operation in operations:
            if not operation():
                self.ui.failed()
                break
            self.ui.header()
        else:
            self.ui.passed()

        if not self.keep:
            self.dispose()

    def _lookup(self):
        operations = [self.check_genpolls, self.check_checkout, self.check_compile, self.check_test]
        init = True
        pass_tests = False
        lookup = self.lookup

        for n in range(self.lookup):
            self.ui.lookup(n+1)
            for operation in operations:
                if not operation():
                    break
                if init:
                    init = False
                    operations = [self.check_genpolls, self.check_test]
                self.ui.header()
            else:
                self.ui.passed()
                pass_tests = True

            if pass_tests:
                self.lookup = None
                break
            elif n+1 == lookup:
                self.ui.failed()
            elif n+1 == (lookup-1):
                self.lookup = None

        self.lookup = lookup

        if not self.keep:
            self.dispose()

    def check_genpolls(self):
        genpolls = GenPolls(name="genpolls", configs=self.configs, challenge=self.current, count=self.count)
        out, err = genpolls()

        if err:
            if self.suppress_assertion and 'AssertionError' in err:
                self.ui.warn(operation="Genpolls", msg=err)
                return True
            self.ui.fail(operation="Genpolls", msg=err)

            if self.persistent:
                self.exclude_challenge(msg="generating polls failed")

            return False

        self.ui.ok(operation="Genpolls", msg=f"(generated {genpolls.count} polls)")
        return True

    def check_checkout(self):
        checkout_cmd = Checkout(name="checkout", configs=self.configs, working_directory=self.working_dir,
                                         challenge=self.current, sanity_check=True)
        out, err = checkout_cmd()

        if err:
            self.ui.fail(operation="Checkout", msg=err)
            return False

        self.ui.ok(operation="Checkout")
        return True

    def check_compile(self):
        compile_cmd = compile.Compile(name="compile", configs=self.configs, working_directory=self.working_dir,
                                      challenge=self.current, inst_files=None, fix_files=None, exit_err=False,
                                      log_file=self.log_file, sanity_check=True)
        compile_cmd.verbose = True
        out, err = compile_cmd()

        if err:
            self.ui.fail(operation="Compile", msg=err)

            return False

        self.ui.ok(operation="Compile")
        return True

    def check_test(self):
        self.status(f"Testing with timeout {self.timeout}.")
        test_cmd = test.Test(name="test", configs=self.configs, working_directory=self.working_dir, update=self.persistent,
                             challenge=self.current, timeout=self.timeout, log_file=self.log_file, neg_pov=True,
                             exit_fail=self.strict)

        test_outcome = test_cmd(save=True, stop=self.strict)
        neg_fails, pos_fails, passing, fails = [], [], [], []

        for test_name, test_result in test_outcome.items():
            if test_result.passed == 0 or test_result.code != 0:
                fails.append(f"{test_name} {test_result.passed}")

                if test_result.is_pov:
                    neg_fails.append(test_name)
                else:
                    pos_fails.append(test_name)
            else:
                passing.append(f"{test_name} {test_result.passed}")

        if not test_outcome or fails:
            self.ui.fail(operation="Test", msg=fails)
            self.ui.ok(operation="Test", msg=passing)

            if self.persistent:
                self.load_metadata()
                if neg_fails:
                    self.exclude_challenge(msg=f"POVs {neg_fails} not working properly")
                elif pos_fails:
                    self.exclude_challenge(msg=f"Polls {pos_fails} not working properly")
                self.save_metadata()

            return False

        self.ui.ok(operation="Test")
        return True

    def exclude_challenge(self, msg: AnyStr):
        if self.lookup and self.genpolls:
            return None
        self.global_metadata[self.current]["excluded"] = True
        self.status(f"Challenge {self.current} excluded: {msg}", warn=True)

    def __str__(self):
        check_cmd_str = " --challenges " + ' '.join(self.challenges)
        check_cmd_str += f" --timeout {self.timeout}"
        check_cmd_str += f" --count {self.count}"

        if self.persistent:
            check_cmd_str += f" --persistent"

        if self.genpolls:
            check_cmd_str += f" --genpolls"

        return super().__str__() + check_cmd_str + "\n"


def check_args(input_parser):
    input_parser.add_argument('--timeout', type=int, default=60, help='The timeout for tests in seconds.')
    input_parser.add_argument('--count', type=int, default=10, help='Number of polls to generate.')
    input_parser.add_argument('--genpolls', action='store_true', help='Flag for enabling polls generation.')
    input_parser.add_argument('--lookup', type=int, default=None, help='Useful for generating polls that pass.')
    input_parser.add_argument('--keep', action='store_true', help='Keeps the files generated.')
    input_parser.add_argument('-sa', '--suppress_assertion', action='store_true',
                              help='Flag for suppressing assertion errors during polls generation.')
    input_parser.add_argument('--strict', action='store_true', help='Stops testing at the first fail.')
    input_parser.add_argument('--persistent', action='store_true',
                              help="Flag for excluding challenges that fail and persist results in the metadata.")


info_parser = add_task("sanity", Sanity, description="Sanity checks for challenges.")
check_args(info_parser)
