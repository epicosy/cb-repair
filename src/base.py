#!/usr/bin/env python3

from pathlib import Path
from config import Configuration
from utils.ui.terminal import TermPrint


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

        if not self.configuration.metadata.exists() and self.name != 'init':
            self.status("Benchmark not initialized", warn=True)
            exit(2)

        if kwargs:
            self.log(f"Unknown arguments: {kwargs}\n")

    def get_challenges(self):
        return self.configuration.get_challenges()

    def get_lib_paths(self):
        return self.configuration.lib_paths

    def get_tools(self):
        return self.configuration.tools

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
