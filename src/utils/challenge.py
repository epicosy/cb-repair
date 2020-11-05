#!/usr/bin/env python3

import re

from pathlib import Path
from typing import List, AnyStr

from .metadata.manifest import Manifest
from .metadata.source_file import SourceFile
from .exceptions import TestNotFound, IncorrectTestNameFormat
from .paths import ChallengePaths

TEST_NAME_FORMAT = "(^(p|n)\d{1,4}$)"


class Challenge:
    def __init__(self, paths: ChallengePaths):
        self.paths = paths
        self.name = paths.name
        self.pos_tests = {}
        self.neg_tests = {}

    def get_manifest(self, source_path: Path = None):
        return Manifest(source_path if source_path else self.paths.source)

    def get_manifest_file(self):
        manifest_file = self.paths.source / Path('manifest')

        if not manifest_file.exists():
            manifest = self.get_manifest()
            manifest.write()

        return manifest_file

    def remove_patches(self, source: Path):
        manifest_file = self.get_manifest_file()

        with manifest_file.open(mode='r') as mf:
            files = mf.read().splitlines()

            for file in files:
                src_file = SourceFile(source / Path(file))
                src_file.remove_patch()

    def get_test(self, test: str):
        match = re.search(TEST_NAME_FORMAT, test)

        if not match:
            raise IncorrectTestNameFormat(f"Test {test} doesnt match format.")

        is_pov = (match.group(2) == 'n')
        # TODO: fix this, working directory should not used it, povs should be previously compiled
        tests = self.neg_tests if is_pov else self.pos_tests

        if test not in tests:
            print(tests)
            raise TestNotFound(f"Test {test} not found in {self.name} set of tests.")

        return Path(tests[test]), is_pov

    def load_pos_tests(self):
        if self.pos_tests == {}:
            tests = self.paths.get_polls()
            len_tests = len(tests)
            tests.sort()
            # Map cases to tests names where p is for positive test cases
            tests_id = [f"p{n}" for n in range(1, len_tests + 1)]
            self.pos_tests = dict(zip(tests_id, tests))

    def load_neg_tests(self, povs_path: Path, excluded: List[AnyStr]):
        if self.neg_tests == {}:
            neg_tests = [str(file) for file in povs_path.iterdir() if file.suffix == ".pov" and file.stem not in excluded]
            len_tests = len(neg_tests)
            neg_tests.sort()
            # Map cases to tests names where p is for positive test cases
            tests_id = [f"n{n}" for n in range(1, len_tests + 1)]
            self.neg_tests = dict(zip(tests_id, neg_tests))

    def info(self):
        with self.paths.info.open(mode="r") as f:
            return f.read()
