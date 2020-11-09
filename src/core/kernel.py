#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Tuple, Union

from config import Configuration
from utils.ui.terminal import TermPrint
from utils.command import Command


class Kernel:
    def __init__(self,
                 name: str,
                 configs: Configuration,
                 log_file: str = None,
                 verbose: bool = False,
                 excl: bool = False,
                 **kwargs):
        self.name = name
        self.configs = configs
        self.verbose = verbose
        self.excl = excl
        self.log_file = Path(log_file) if log_file else log_file

        if not self.configs.metadata.exists():
            self.status(f"Not initialized: run ./init.py", warn=True)
            exit(1)

        self.global_metadata = {}
        self.load_metadata()
        self.challenges = [challenge for challenge, metadata in self.global_metadata.items() if not (metadata["excluded"] and not excl)]
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

    def has_challenge(self, challenge_name: str):
        if challenge_name not in self.global_metadata:
            self.status(f"No {challenge_name} challenge", err=True)
            exit(1)

    def is_excluded(self, challenge_name: str):
        if self.global_metadata[challenge_name]['excluded']:
            self.status(f"Challenge {challenge_name} was excluded.", warn=True)

            if not self.excl:
                exit(1)

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

        self.log(message)

    def __str__(self):
        return self.name
