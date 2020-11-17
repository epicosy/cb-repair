#!/usr/bin/env python3

from pathlib import Path

from core.task import Task
from input_parser import add_task


class Clean(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        self.configs.metadata.unlink()

        for challenge in self.challenges:
            self.status(f"Cleaning {challenge}\n")
            challenge_paths = self.configs.lib_paths.get_challenge_paths(challenge)
            for name in ['patch', 'vuln', 'manifest']:
                file = challenge_paths.source / Path(name)

                if file.exists():
                    file.unlink()
                    self.status(f"\tRemoved {name} file\n")

    def __str__(self):
        check_cmd_str = " --challenges " + ' '.join(self.challenges)
        return super().__str__() + check_cmd_str + "\n"


def clean_args(input_parser):
    pass


clean_parser = add_task("clean", Clean, description="Cleans all cache files.")
clean_args(clean_parser)
