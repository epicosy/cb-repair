#!/usr/bin/env python3

from pathlib import Path
from config import Configuration


class Base:
    def __init__(self,
                 name: str,
                 configs: Configuration,
                 log_file: str = None,
                 verbose: bool = False,
                 **kwargs):
        self.name = name
        self.configuration = configs
        self.verbose = verbose
        self.log_file = Path(log_file) if log_file else log_file

        if kwargs:
            self.log(f"Unknown arguments: {kwargs}\n")

    def get_challenges(self):
        return self.configuration.lib_paths.get_challenges()

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
        return self.name
