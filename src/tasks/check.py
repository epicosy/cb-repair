#!/usr/bin/env python3
import json
import os
from pathlib import Path
from typing import List, AnyStr

from base import Base
from input_parser import add_base
from .genpolls import GenPolls
import operations.checkout as checkout
import operations.compile as compile
import operations.test as test


class Check(Base):
    def __init__(self,
                 challenges: List[AnyStr],
                 timeouts: List[AnyStr],
                 count: int,
                 **kwargs):
        super().__init__(**kwargs)
        self.challenges = challenges
        self.results = {}
        self.count = count
        self.timeouts = timeouts
        self.tests_map = {"0": "failed", "1": "passed", "2": "error", "3": "timeout"}

    def __call__(self):
        if not self.challenges:
            self.challenges = self.get_challenges()
            self.challenges.sort()

        lib_paths = self.get_lib_paths()

        try:
            for challenge in self.challenges:
                self.results[challenge] = {"passed": [], "failed": [], "timeout": [], "error": []}
                self.status(f"Checking {challenge}")
                self.check(challenge)
                challenge_paths = lib_paths.get_challenge_paths(challenge)
                out_path = challenge_paths.source / Path("checks.txt")
                pos_out_path = challenge_paths.source / Path("pos_checks.txt")
                neg_out_path = challenge_paths.source / Path("neg_checks.txt")

                with out_path.open("w+") as res, pos_out_path.open("w+") as pos_res, \
                        neg_out_path.open("w+") as neg_res:

                    for test in self.results[challenge]["passed"]:
                        res.write(f"{test} ")

                        if test.startswith("p"):
                            pos_res.write(f"{test} ")
                        else:
                            neg_res.write(f"{test} ")

        except Exception as e:
            self.log_file = Path("check_exception.log")
            self.log(str(e))
            print(e)

        out_path = lib_paths.root / Path("checks.json")

        if out_path.exists():
            with out_path.open(mode="r") as op:
                old = json.loads(op.read())
                for k, v in old.items():
                    if k not in self.results:
                        self.results[k] = v

        with out_path.open("w+") as res:
            json.dump(self.results, res, indent=2)

    def check(self, challenge_name):
        working_dir = f"/tmp/check_{challenge_name}"
        genpolls = GenPolls(name="genpolls", configs=self.configuration, challenge_name=challenge_name,
                            count=self.count)
        genpolls()

        checkout_cmd = checkout.Checkout(name="checkout", configs=self.configuration, working_directory=working_dir,
                                         challenge_name=challenge_name)
        checkout_cmd()
        compile_cmd = compile.Compile(name="compile", configs=self.configuration, working_directory=working_dir,
                                      challenge_name=challenge_name, inst_files=None, fix_files=None)
        compile_cmd()
        tests = None

        for timeout in self.timeouts:
            self.configuration.tests_timeout = timeout
            self.results[challenge_name]["timeout"] = []

            test_cmd = test.Test(name="test", configs=self.configuration, working_directory=working_dir,
                                 challenge_name=challenge_name, tests=tests, write_fail=True, neg_pov=False)

            results = test_cmd(save=True)

            for key, value in results.items():
                self.results[challenge_name][self.tests_map[value]].append(key)

            tests = self.results[challenge_name]["timeout"]

            if not tests:
                break

        # os.system(f"rm -rf {working_dir}")

    def __str__(self):
        pass


def check_args(input_parser):
    input_parser.add_argument('--challenges', type=str, nargs='+', required=False,
                              help='The challenges to be checked.')
    input_parser.add_argument('--timeouts', type=str, nargs='+', required=True,
                              help='The timeouts for tests in seconds.')
    input_parser.add_argument('--count', type=int, required=True, help='The timeouts for tests in seconds.')


info_parser = add_base("check", Check, description="Checks if tests fail or timeout.")
check_args(info_parser)
