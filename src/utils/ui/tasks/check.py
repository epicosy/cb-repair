#!/usr/bin/env python3
import os

from utils.ui.terminal import Colors


class CheckUI:
    def __init__(self):
        self.results = {}
        self.current = None

    def ok(self, operation: str, msg: str = ""):
        if self.current:
            self.results[self.current].append(Colors.ok(f"\t{operation} passed \u2713 {msg}"))

    def fail(self, operation: str, msg: str = ""):
        if self.current:
            self.results[self.current].append(Colors.fail(f"\t{operation} failed \u2713 {msg}"))

    def warn(self, operation: str, msg: str):
        if self.current:
            self.results[self.current].append(Colors.warn(f"\t{operation}: {msg}!"))

    def passed(self):
        if self.current:
            self.results[self.current].insert(0, Colors.ok(f"{self.current} passed \u2713 \n\t└──", ''))

    def failed(self):
        if self.current:
            self.results[self.current].insert(0, Colors.fail(f"{self.current} failed \u2717 \n\t└──", ''))

    def header(self):
        if self.current:
            os.system('clear')
            print(Colors.cyan(f"Checking {self.current}") + '\n'.join(self.results[self.current]))

    def lookup(self, n: int):
        if self.current:
            os.system('clear')
            self.results[self.current].append(Colors.cyan(f"Lookup {n}"))
            print('\n'.join(self.results[self.current]))

    def __call__(self, challenge_name: str):
        self.results[challenge_name] = []
        self.current = challenge_name
        self.header()

    def print(self):
        os.system('clear')
        print(self)

    def __str__(self):
        check_ui_str = ""

        for cn, result in self.results.items():
            check_ui_str += result[0] + '\t'.join(result[1:])

        return check_ui_str
