#!/usr/bin/env python3

import json
from typing import List, AnyStr

from base import Base
from input_parser import add_base
from utils.ui.terminal import progress


class Init(Base):
    def __init__(self, challenges: List[AnyStr], **kwargs):
        super().__init__(**kwargs)
        self.challenges = challenges

        if not self.challenges:
            self.challenges = self.get_challenges()
            self.challenges.sort()

    def __call__(self):
        if self.configuration.metadata.exists():
            self.status('Benchmark already initialized', bold=True)
        else:
            metadata = {}
            challenges_count = len(self.challenges)

            for i, challenge in enumerate(self.challenges):
                metadata[challenge] = {'excluded': False, "excluded_neg_tests": []}
                progress(i, challenges_count, challenge)
            with self.configuration.metadata.open(mode='w') as mf:
                json.dump(metadata, mf, indent=2)

            self.status('Benchmark initialized', ok=True)

    def __str__(self):
        check_cmd_str = " --challenges " + ' '.join(self.challenges)
        return super().__str__() + check_cmd_str + "\n"


def init_args(input_parser):
    input_parser.add_argument('--challenges', type=str, nargs='+', required=False,
                              help='The challenges to be cleaned.')


init_parser = add_base("init", Init, description="Initializes framework.")
init_args(init_parser)
