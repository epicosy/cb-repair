#!/usr/bin/env python3
import json
from dataclasses import dataclass
from os.path import dirname, abspath
from pathlib import Path

from utils.paths import LibPaths, Tools

ROOT_DIR = dirname(dirname(__file__))
SOURCE_DIR = dirname(abspath(__file__))


@dataclass
class Configuration:
    root: Path
    src: Path
    lib_paths: LibPaths
    tools: Tools
    metadata: Path
    tests_timeout: str  # In seconds

    def validate(self):
        return self.src.exists() and self.lib_paths.validate() and self.metadata.exists() \
               and self.tools.validate() and int(self.tests_timeout) > 0

    def get_metadata(self, challenge_name: str = None) -> dict:
        with self.metadata.open(mode="r") as m:
            md = json.load(m)

            if challenge_name:
                if challenge_name in md:
                    return md[challenge_name]
                return {}
            return md

    def save_metadata(self, new_metadata: dict):
        with self.metadata.open(mode="w") as m:
            json.dump(new_metadata, m, indent=2)

    def get_challenges(self, excluded: bool = False):
        if not excluded:
            return [challenge for challenge, _metadata in self.get_metadata().items() if not _metadata["excluded"]]
        return [challenge for challenge, _metadata in self.get_metadata().items()]


lib_path = Path(ROOT_DIR) / Path("lib")
tools_path = Path(ROOT_DIR) / Path("tools")
metadata = lib_path / Path("metadata")
lib_paths = LibPaths(root=lib_path,
                     polls=lib_path / Path("polls"),
                     challenges=lib_path / Path("challenges"))

tools = Tools(root=tools_path,
              cmake_file=tools_path / Path("CMakeLists.txt"),
              cmake_file_no_patch=tools_path / Path("CMakeListsNoPatch.txt"),
              compile=tools_path / Path("compile.sh"),
              test=tools_path / Path("cb-test.py"),
              gen_polls=tools_path / Path("generate-polls", "generate-polls"),
              scores=tools_path / Path('cwe_scores.pkl'))

configuration = Configuration(root=Path(ROOT_DIR),
                              src=Path(ROOT_DIR) / Path(SOURCE_DIR),
                              lib_paths=lib_paths,
                              tools=tools,
                              metadata=metadata,
                              tests_timeout="10")
