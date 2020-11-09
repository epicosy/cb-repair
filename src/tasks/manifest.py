#!/usr/bin/env python3

from core.task import Task
from input_parser import add_task


class Manifest(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        for challenge in self.challenges:
            manifest_file = self.challenge.get_manifest_file()
            print(challenge, str(manifest_file))


def manifest_args(input_parser):
    pass


info_parser = add_task("manifest", Manifest, description="Lists files containing vulnerabilities.")
manifest_args(info_parser)
