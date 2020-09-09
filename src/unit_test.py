#!/usr/bin/env python3

import unittest
from pathlib import Path

from config import configuration
from operations.checkout import Checkout
from operations.compile import Compile
from operations.test import Test

CHALLENGE = "BitBlaster"
WORKING_DIRECTORY = "/tmp/test" + CHALLENGE


class TestOperations(unittest.TestCase):
    def setUp(self):
        self.opr = Checkout(name="checkout",
                            configs=configuration,
                            working_directory=WORKING_DIRECTORY,
                            challenge_name=CHALLENGE,
                            verbose=True)

    def test_checkout(self):
        self.opr()
        self.assertTrue(self.opr.working_dir.exists())
        self.assertTrue(self.opr.source.exists())
        self.assertTrue((self.opr.working_dir / Path("include")).exists())
        self.assertTrue((self.opr.working_dir / Path("CMakeLists.txt")).exists())
        self.assertTrue(self.opr.compile_script.exists())

    def test_compile(self):
        self.opr = Compile(name="compile",
                           configs=configuration,
                           working_directory=WORKING_DIRECTORY,
                           challenge_name=CHALLENGE,
                           inst_files=None,
                           fix_file=None,
                           verbose=True)
        self.opr()
        self.assertTrue(self.opr.build.exists())
        self.assertTrue(self.opr.commands_path.exists())
        self.assertTrue((self.opr.build / Path(f"{CHALLENGE}")).exists())
        self.assertTrue((self.opr.build / Path(f"{CHALLENGE}_patched")).exists())
        self.assertTrue((self.opr.build / Path("pov_1.pov")).exists())

    def test_poll(self):
        self.opr = Test(name="test",
                        configs=configuration,
                        working_directory=WORKING_DIRECTORY,
                        challenge_name=CHALLENGE,
                        port=None,
                        exit_fail=True,
                        write_fail=True,
                        tests=["p1"],
                        out_file=WORKING_DIRECTORY + "/result_p1.txt",
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
                        working_directory=WORKING_DIRECTORY,
                        challenge_name=CHALLENGE,
                        port=None,
                        exit_fail=True,
                        tests=["n1"],
                        out_file=WORKING_DIRECTORY + "/result_n1.txt",
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
    unittest.main()
