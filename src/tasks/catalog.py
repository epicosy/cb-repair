#!/usr/bin/env python3

from core.task import Task
from input_parser import add_task


class Catalog(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        for challenge in self.challenges:
            print(challenge)

    def __str__(self):
        pass


def catalog_args(input_parser):
    pass


info_parser = add_task("catalog", Catalog, description="List's benchmark challenges.")
catalog_args(info_parser)
