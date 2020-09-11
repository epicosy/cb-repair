#!/usr/bin/env python3

import unittest
from pathlib import Path

from config import configuration
from operations.checkout import Checkout
from operations.compile import Compile
from operations.test import Test
import tasks.genpolls

WORKING_DIRECTORY = "/tmp/test"

challlenges = configuration.lib_paths.get_challenges()
configuration.tests_timeout = "10"


class TestOperations(unittest.TestCase):
    challenge = ""

    @classmethod
    def setUpClass(cls):
        cls.working_dir = WORKING_DIRECTORY + cls.challenge
        print(f"Testing Challenge {cls.challenge}\n:")

    def test_agenpolls(self):
        self.opr = tasks.genpolls.GenPolls(name="genpolls",
                                           configs=configuration,
                                           challenge_name=self.challenge,
                                           count=5,
                                           verbose=True)
        self.opr()
        self.assertTrue(self.opr.challenge.paths.polls.exists())
        self.assertTrue(self.opr.out_dir.exists())

    def test_checkout(self):
        self.opr = Checkout(name="checkout",
                            configs=configuration,
                            working_directory=self.working_dir,
                            challenge_name=self.challenge,
                            verbose=True)
        self.opr()
        self.assertTrue(self.opr.working_dir.exists())
        self.assertTrue(self.opr.source.exists())
        self.assertTrue((self.opr.working_dir / Path("include")).exists())
        self.assertTrue((self.opr.working_dir / Path("CMakeLists.txt")).exists())
        self.assertTrue(self.opr.compile_script.exists())

    def test_compile(self):
        self.opr = Compile(name="compile",
                           configs=configuration,
                           working_directory=self.working_dir,
                           challenge_name=self.challenge,
                           inst_files=None,
                           fix_file=None)

        self.opr()
        self.assertTrue(self.opr.build.exists())
        self.assertTrue(self.opr.commands_path.exists())
        self.assertTrue((self.opr.build / Path(f"{self.challenge}")).exists())
        self.assertTrue((self.opr.build / Path(f"{self.challenge}_patched")).exists())
        self.assertTrue((self.opr.build / Path("pov_1.pov")).exists())

    def test_poll(self):
        self.opr = Test(name="test",
                        configs=configuration,
                        working_directory=self.working_dir,
                        challenge_name=self.challenge,
                        port=None,
                        exit_fail=True,
                        write_fail=True,
                        tests=["p1"],
                        out_file=self.working_dir + "/result_p1.txt",
                        verbose=True)

        with self.assertRaises(SystemExit) as se:
            self.opr()

        self.assertEqual(se.exception.code, 0)
        self.assertTrue(self.opr.out_file.exists())

        with self.opr.out_file.open(mode="r") as of:
            result = of.readline().split("\n")[0]
            self.assertEqual(result, "p1 1")
        self.opr.out_file.unlink()

    def test_pov(self):
        self.opr = Test(name="test",
                        configs=configuration,
                        working_directory=self.working_dir,
                        challenge_name=self.challenge,
                        port=None,
                        exit_fail=True,
                        tests=["n1"],
                        out_file=self.working_dir + "/result_n1.txt",
                        write_fail=True,
                        verbose=True)

        with self.assertRaises(SystemExit) as se:
            self.opr()

        self.assertEqual(se.exception.code, 1)
        self.assertTrue(self.opr.out_file.exists())

        with self.opr.out_file.open(mode="r") as of:
            result = of.readline().split("\n")[0]
            self.assertEqual(result, "n1 0")


if __name__ == "__main__":

    for chal in challlenges:
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        test = TestOperations
        test.challenge = chal

        tests = loader.loadTestsFromTestCase(test)
        suite.addTest(tests)
        results = unittest.TextTestRunner().run(suite)

        with open("unit_tests_results.txt", "a") as res:
            res.write(f"Challenge: {chal}\n")
            res.write(f"\t--Tests Run: {str(results.testsRun)}\n")
            res.write(f"\t--Failures: {str(results.failures)}\n")
            res.write(f"\t--Errors: {str(results.errors)}\n")

        break
