#!/usr/bin/env python3

from context import Context
from utils.command import Command
from typing import Tuple, Union


class Operation(Context):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

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

    def __str__(self):
        prefix_cmd = (f' -pf ' + self.prefix) if self.prefix is not None else ""
        return f"{self.name} -wd {self.working_dir} -cn {self.challenge.name}" + prefix_cmd
