#!/usr/bin/env python3

from core.operation import Operation
from input_parser import add_operation


class Info(Operation):
    def __init__(self, task: str, **kwargs):
        super().__init__(**kwargs)
        self.task = task

    def __call__(self):
        if self.task == "prefix":
            self._set_build_paths()

            print(self.cmake)

        elif self.task == "count_tests":
            self._set_build_paths()
            self.challenge.load_pos_tests()

            if self.build.exists():
                self.challenge.load_neg_tests(self.build)
                print(f"{self.challenge.neg_tests} ")
            else:
                neg_tests = [pd for pd in self.source.iterdir() if pd.match("pov*") and pd.is_dir()]
                print(f"{len(self.challenge.pos_tests)} {len(neg_tests)} ")
        else:
            print(self.challenge.info())


def info_args(input_parser):
    input_parser.add_argument('-t', '--task', help='Info related task to be executed.',
                              choices=["prefix", "count_tests"], type=str, default=None)


info_parser = add_operation("info", Info, 'Query information about the benchmark challenges.')
info_args(info_parser)
