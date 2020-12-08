#!/usr/bin/env python3
import json
from os import environ
from pathlib import Path
from typing import Tuple, Union

from config import Configuration
from utils.ui.terminal import TermPrint
from utils.command import Command
from utils.challenge import Challenge


class Kernel:
    def __init__(self,
                 name: str,
                 configs: Configuration,
                 log_file: str = None,
                 verbose: bool = False,
                 no_status: bool = False,
                 excl: bool = False,
                 **kwargs):
        self.name = name
        self.configs = configs
        self.verbose = verbose
        self.no_status = no_status
        self.env = None
        self.excl = excl
        self.log_file = Path(log_file) if log_file else log_file
        self.output, self.error = None, None

        if not self.configs.metadata.exists():
            self.status(f"Not initialized: run ./init.py", warn=True)
            exit(1)

        self.global_metadata = {}
        self.load_metadata()
        self.challenges = [challenge for challenge, metadata in self.global_metadata.items() if
                           not (metadata["excluded"] and not excl)]
        self.challenges.sort()

        if kwargs:
            self.log(f"Unknown arguments: {kwargs}\n")

    def __call__(self,
                 cmd_str: str,
                 timeout: int = None,
                 exit_err: bool = False,
                 cmd_cwd: str = None,
                 msg: str = None) -> Tuple[Union[str, None], Union[str, None]]:
        if msg:
            if not self.no_status:
                print(msg)
            if self.verbose:
                print(cmd_str)

        self.log(msg)
        self.log(f"Command: {cmd_str}\n")

        cmd = Command(cmd_str, cwd=cmd_cwd)

        self.output, self.error = cmd(verbose=self.verbose, timeout=timeout, env=self.env, exit_err=exit_err,
                                      file=self.log_file)
        return self.output, self.error

    def set_env(self):
        self.env = environ.copy()

    def has_challenge(self, challenge_name: str):
        if challenge_name not in self.global_metadata:
            self.status(f"No {challenge_name} challenge", err=True)
            exit(1)

    def is_excluded(self, challenge_name: str):
        if self.global_metadata[challenge_name]['excluded']:
            self.status(f"Challenge {challenge_name} was excluded.", warn=True)

            if not self.excl:
                exit(1)

    def get_challenge(self, challenge_name: str):
        # Check if challenge is valid
        self.has_challenge(challenge_name)
        self.is_excluded(challenge_name)
        # Generate Paths
        paths = self.get_challenge_paths(challenge_name)

        return Challenge(paths, metadata=self.global_metadata[challenge_name])

    def get_challenge_paths(self, challenge_name: str):
        return self.configs.lib_paths.get_challenge_paths(challenge_name)

    def get_lib_paths(self):
        return self.configs.lib_paths

    def get_tools(self):
        return self.configs.tools

    def load_metadata(self):
        with self.configs.metadata.open(mode="r") as m:
            self.global_metadata = json.load(m)

    def save_metadata(self, new_metadata: dict):
        with self.configs.metadata.open(mode="w") as m:
            json.dump(new_metadata, m, indent=2)

    def log(self, msg: str):
        if self.log_file and msg:
            with self.log_file.open(mode="a") as lf:
                lf.write(msg)

    def status(self, message: str, err: bool = False, bold: bool = False, ok: bool = False, warn: bool = False,
               nan: bool = False):
        self.log(message)

        if self.no_status:
            return

        if ok:
            TermPrint.print_pass(message)
        elif err:
            TermPrint.print_fail(message)
        elif bold:
            TermPrint.print_bold(message)
        elif warn:
            TermPrint.print_warn(message)
        elif nan:
            print(message)
        else:
            TermPrint.print_info(message)

    def __str__(self):
        return self.name
