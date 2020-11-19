#!/usr/bin/env python3


from core.task import Task
from input_parser import add_task
from operations.simple.genpolls import GenPolls


class InitPolls(Task):
    def __init__(self, count: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count

    def __call__(self):
        for challenge in self.challenges:
            genpolls = GenPolls(name="genpolls", configs=self.configs, challenge=challenge, count=self.count)
            out, err = genpolls()

    def __str__(self):
        return super().__str__()


def init_polls_args(input_parser):
    input_parser.add_argument('--count', type=int, default=10, help='Number of polls to generate.')


init_polls_parser = add_task("init_polls", InitPolls, description="Inits polls for all challenges.")
init_polls_args(init_polls_parser)
