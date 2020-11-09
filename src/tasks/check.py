#!/usr/bin/env python3

import os
import traceback

from pathlib import Path
from typing import AnyStr, Dict

import operations.checkout as checkout
import operations.compile as compile
import operations.test as test

from core.task import Task
from input_parser import add_task
from utils.ui.tasks.check import CheckUI
from operations.simple.genpolls import GenPolls


class Check(Task):
    def __init__(self, timeout: int, genpolls: bool, sanity: bool, count: int, **kwargs):
        super().__init__(**kwargs)
        self.current = None
        self.working_dir = None
        self.genpolls = genpolls
        self.sanity = sanity
        self.count = count
        self.timeout = timeout
        self.ui = CheckUI()

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
                self.check()
                os.system('clear')
                self.ui.print()
        except Exception as e:
            self.dispose()
            self.log_file = Path("check_exception.log")
            self.status(traceback.format_exc(), err=True)
        finally:
            if self.sanity:
                self.save_metadata(self.global_metadata)

    def dispose(self):
        os.system(f"rm -rf {self.working_dir}")
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

        self.dispose()

    def check_genpolls(self):
        genpolls = GenPolls(name="genpolls", configs=self.configs, challenge=self.current, count=self.count)
        out, err = genpolls()

        if err:
            self.ui.fail(operation="Genpolls", msg=err)

            if self.sanity:
                self.exclude_challenge(msg="generating polls failed")

            return False

        self.ui.ok(operation="Genpolls", msg=f"(generated {genpolls.count} polls)")
        return True

    def check_checkout(self):
        checkout_cmd = checkout.Checkout(name="checkout", configs=self.configs, working_directory=self.working_dir,
                                         challenge=self.current)
        out, err = checkout_cmd()

        if err:
            self.ui.fail(operation="Checkout", msg=err)
            return False

        self.ui.ok(operation="Checkout")
        return True

    def check_compile(self):
        compile_cmd = compile.Compile(name="compile", configs=self.configs, working_directory=self.working_dir,
                                      challenge=self.current, inst_files=None, fix_files=None, exit_err=False)
        compile_cmd.verbose = True
        out, err = compile_cmd()

        if err:
            self.ui.fail(operation="Compile", msg=err)

            return False

        self.ui.ok(operation="Compile")
        return True

    def check_test(self):
        self.status(f"Testing with timeout {self.timeout}.")
        test_cmd = test.Test(name="test", configs=self.configs, working_directory=self.working_dir,
                             challenge=self.current, write_fail=True, neg_pov=False, timeout=self.timeout)

        test_outcome = test_cmd(save=True)
        neg_fails, passing, fails = [], [], []

        for test_name, outcome in test_outcome.items():
            if outcome != '1':
                fails.append(f"{test_name} {outcome}")
                if test_name.starts_with('n'):
                    neg_fails.append(test_name)
            else:
                passing.append(f"{test_name} {outcome}")

        if not test_outcome or fails:
            self.ui.fail(operation="Test", msg=fails)
            self.ui.ok(operation="Test", msg=passing)

            if self.sanity and neg_fails:
                self.test_sanity({True if k in neg_fails else False: Path(v) for k, v in test_cmd.challenge.neg_tests.items()})

            return False

        self.ui.ok(operation="Test")
        return True

    def test_sanity(self, povs_outcome: Dict[bool, Path]):
        if list(povs_outcome.keys()).count(False) == 0:
            self.exclude_challenge(msg="POVs not working properly")
        else:
            for failed, path in povs_outcome.items():
                if failed:
                    print(path.stem)
                    self.global_metadata[self.current]["excluded_neg_tests"].append(path.stem)
                    self.ui.warn(operation="Test", msg=f"POV {path.stem} excluded")

    def exclude_challenge(self, msg: AnyStr):
        self.global_metadata[self.current]["excluded"] = True
        self.status(f"Challenge {self.current} excluded: {msg}", warn=True)

    def __str__(self):
        check_cmd_str = " --challenges " + ' '.join(self.challenges)
        check_cmd_str += f" --timeout {self.timeout}"
        check_cmd_str += f" --count {self.count}"

        if self.sanity:
            check_cmd_str += f" --sanity"

        if self.genpolls:
            check_cmd_str += f" --genpolls"

        return super().__str__() + check_cmd_str + "\n"


def check_args(input_parser):
    input_parser.add_argument('--timeout', type=int, default=60, help='The timeout for tests in seconds.')
    input_parser.add_argument('--count', type=int, default=10, help='Number of polls to generate.')
    input_parser.add_argument('--genpolls', action='store_true', help='Flag for enabling polls generation.')
    input_parser.add_argument('--sanity', action='store_true',
                              help="Flag for removing challenges that fail generating polls or POVs that don't work.")


info_parser = add_task("check", Check, description="Sanity checks for challenges.")
check_args(info_parser)
