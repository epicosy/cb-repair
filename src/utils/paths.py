#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Tools:
    root: Path
    cmake_file: Path
    cmake_file_no_patch: Path
    compile: Path
    test: Path
    gen_polls: Path
    scores: Path

    def validate(self):
        return self.root.exists() and self.cmake_file.exists() \
               and self.cmake_file_no_patch.exists() and self.compile.exists() \
               and self.gen_polls.exists() and self.test.exists() and self.scores.exists()


@dataclass
class ChallengePaths:
    name: str
    source: Path
    info: Path
    polls: Path
    poller: Path

    def get_polls(self):
        for_release = self.polls / Path('for-release')
        for_testing = self.polls / Path('for-testing')
        polls = []

        if for_release.exists():
            polls.extend(str(file) for file in for_release.iterdir() if file.suffix == ".xml")
        if for_testing.exists():
            polls.extend(str(file) for file in for_testing.iterdir() if file.suffix == ".xml")

        return polls

    def get_povs(self):
        return [f.name for f in self.source.iterdir() if f.is_dir() and f.name.startswith('pov')]


@dataclass
class LibPaths:
    root: Path
    polls: Path
    challenges: Path

    def validate(self):
        return self.root.exists() and self.polls.exists() \
               and self.challenges.exists()

    def get_challenges(self):
        return [challenge.name for challenge in self.challenges.iterdir() if challenge.is_dir()]

    def get_polls_path(self, challenge_name: str):
        return self.polls / Path(challenge_name, 'poller')

    def get_challenge_paths(self, challenge_name):
        source = self.challenges / Path(challenge_name)
        readme = source / Path("README.md")
        polls = self.polls / Path(challenge_name, 'poller')
        poller = self.challenges / Path(challenge_name, 'poller')

        return ChallengePaths(challenge_name, source, readme, polls, poller)
