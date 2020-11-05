#!/usr/bin/env python3

from pathlib import Path
from typing import List, AnyStr

from base import Base
from input_parser import add_base


class Clean(Base):
    def __init__(self, challenges: List[AnyStr], **kwargs):
        super().__init__(**kwargs)
        self.challenges = challenges

        if not self.challenges:
            self.challenges = self.get_challenges()
            self.challenges.sort()

    def __call__(self):
        self.configuration.metadata.unlink()

        for challenge in self.challenges:
            self.status(f"Cleaning {challenge}\n")
            challenge_paths = self.configuration.lib_paths.get_challenge_paths(challenge)
            for name in ['patch', 'vuln', 'manifest']:
                file = challenge_paths.source / Path(name)

                if file.exists():
                    file.unlink()
                    self.status(f"\tRemoved {name} file\n")

    def __str__(self):
        check_cmd_str = " --challenges " + ' '.join(self.challenges)
        return super().__str__() + check_cmd_str + "\n"


def clean_args(input_parser):
    input_parser.add_argument('--challenges', type=str, nargs='+', required=False,
                              help='The challenges to be cleaned.')


clean_parser = add_base("clean", Clean, description="Cleans all cache files.")
clean_args(clean_parser)
