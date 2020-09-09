#!/usr/bin/env python3

from pathlib import Path

from config import Configuration
from utils.paths import *
from utils.exceptions import ChallengeNotFound
from utils.challenge import Challenge


class Setting:
    def __init__(self,
                 challenge_name: str,
                 configs: Configuration,
                 log_file: str = None,
                 verbose: bool = False,
                 **kwargs):
        self.configuration = configs
        self._set_challenge(challenge_name)
        self.verbose = verbose
        self.log_file = Path(log_file) if log_file else log_file

        if kwargs:
            self.status(f"Unknown arguments: {kwargs}\n")

    def _set_challenge(self, challenge_name: str):
        challenges = self.configuration.lib_paths.get_challenges()

        if challenge_name not in challenges:
            raise ChallengeNotFound("No such challenge")

        challenge_paths = self.configuration.lib_paths.get_challenge_paths(challenge_name)

        self.challenge = Challenge(challenge_paths)

    def get_lib_paths(self):
        return self.configuration.lib_paths

    def get_tools(self):
        return self.configuration.tools

    def log(self, msg: str):
        if self.log_file is not None:
            with self.log_file.open(mode="a") as lf:
                lf.write(msg)

    def status(self, message: str):
        print(message)
        self.log(message)
