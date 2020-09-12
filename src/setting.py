#!/usr/bin/env python3

from pathlib import Path

from utils.paths import *
from utils.exceptions import ChallengeNotFound
from utils.challenge import Challenge
from utils.command import Command
from typing import Tuple, Union
from base import Base


class Setting(Base):
    def __init__(self,
                 challenge_name: str,
                 **kwargs):
        super().__init__(**kwargs)
        self._set_challenge(challenge_name)

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
        challenges = self.get_challenges()

        if challenge_name not in challenges:
            raise ChallengeNotFound("No such challenge")

        challenge_paths = self.configuration.lib_paths.get_challenge_paths(challenge_name)

        self.challenge = Challenge(challenge_paths)

    def get_lib_paths(self):
        return self.configuration.lib_paths

    def get_tools(self):
        return self.configuration.tools

    def __str__(self):
        return super().__str__() + f" -cn {self.challenge.name}"
