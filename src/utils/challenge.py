#!/usr/bin/env python3
import json
import re

from pathlib import Path
from typing import List, AnyStr, Union

from .metadata.manifest import Manifest
from .metadata.source_file import SourceFile
from .exceptions import TestNotFound, IncorrectTestNameFormat
from .paths import ChallengePaths
from .parse import cwe_from_info
from .cwe_dictionary import main_cwe, get_name, top_parent

TEST_NAME_FORMAT = r"(^(p|n)\d{1,4}$)"


class Challenge:
    def __init__(self, paths: ChallengePaths, metadata: dict):
        self.paths = paths
        self.name = paths.name
        self.metadata = metadata
        self.pos_tests = {}
        self.neg_tests = {}

    def get_manifest(self, source_path: Path = None, force: bool = False):
        path = source_path if source_path else self.paths.source
        manifest_file = path / Path('manifest')

        if not manifest_file.exists():
            manifest = Manifest(path)
            manifest.write()
            return manifest_file, manifest

        return manifest_file, Manifest(path) if force else None

    def remove_patches(self, source: Path):
        manifest_file, _ = self.get_manifest()
        vuln_file = source / Path("vuln")
        new_vuln = {}

        with manifest_file.open(mode='r') as mf:
            files = mf.read().splitlines()

            for file in files:
                src_file = SourceFile(source / Path(file))
                src_file.remove_patch()
                new_vuln.update({file: src_file.get_vuln()})

        with vuln_file.open(mode='w') as vf:
            json.dump(new_vuln, vf, indent=2)

    def get_test(self, test: str):
        match = re.search(TEST_NAME_FORMAT, test)

        if not match:
            raise IncorrectTestNameFormat(f"Test {test} doesnt match format.")

        is_pov = match.group(2) == 'n'
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

    def load_neg_tests(self, povs_path: Path):
        if self.neg_tests == {}:
            neg_tests = [str(file) for file in povs_path.iterdir() if file.suffix == ".pov"]
            len_tests = len(neg_tests)
            len_pos = len(self.pos_tests)
            neg_tests.sort()
            # Map cases to tests names where p is for positive test cases
            tests_id = [f"n{n}" for n in range(1, len_tests + 1)]
            self.neg_tests = dict(zip(tests_id, neg_tests))

    def info(self):
        with self.paths.info.open(mode="r") as f:
            return f.read()

    def cwe_ids(self, number: bool = True) -> List[Union[int, str]]:
        description = self.info()

        if number:
            return [int(cwe.split('-')[1]) for cwe in cwe_from_info(description)]
        else:
            return [cwe for cwe in cwe_from_info(description)]

    def cwe_type(self):
        ids = self.cwe_ids()
        main = main_cwe(ids, count=3)

        return f"CWE-{main}: {get_name(main)}"

    def get_cwes(self, parent: bool = False, name: bool = False) -> List[Union[str, int]]:
        ids = self.cwe_ids()

        if parent:
            ids = [top_parent(id, None, count=3) for id in ids]

        if name:
            ids = [f"CWE-{id} {get_name(id)}" for id in ids]

        return ids

    def stats(self):
        return {
            'povs': len(self.paths.get_povs()),
            'lines': self.metadata['lines'],
            'vuln_lines': self.metadata['vuln_lines'],
            'patch_lines': self.metadata['patch_lines'],
            'cwes': self.get_cwes(parent=True, name=True)
        }
