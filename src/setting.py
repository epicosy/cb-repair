#!/usr/bin/env python3

from pathlib import Path

from config import Configuration
from utils.paths import *
from utils.exceptions import ChallengeNotFound
from utils.challenge import Challenge
from utils.command import Command
from typing import Tuple, Union


class Setting:
    def __init__(self,
                 name: str,
                 challenge_name: str,
                 configs: Configuration,
                 log_file: str = None,
                 verbose: bool = False,
                 **kwargs):
        self.name = name
        self.configuration = configs
        self._set_challenge(challenge_name)
        self.verbose = verbose
        self.log_file = Path(log_file) if log_file else log_file

        if kwargs:
            self.status(f"Unknown arguments: {kwargs}\n")

    def __call__(self,
                 cmd_str: str,
                 timeout: int = None,
                 exit_err: bool = False,
                 cmd_cwd: str = None,
                 msg: str = None) -> Tuple[Union[str, None], Union[str, None]]:
        if msg:
            print(msg)
            if self.verbose:
                print(cmd_str)

        self.log(msg)
        self.log(f"Command: {cmd_str}\n")

        cmd = Command(cmd_str, cwd=cmd_cwd)

        out, err = cmd(verbose=self.verbose,
                       timeout=timeout,
                       exit_err=exit_err,
                       file=self.log_file)
        return out, err

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

    def __str__(self):
        return f"{self.name} -cn {self.challenge.name}"
