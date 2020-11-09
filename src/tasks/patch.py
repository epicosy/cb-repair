#!/usr/bin/env python3
import json
from pathlib import Path

from core.task import Task
from input_parser import add_task


class Patch(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        for challenge in self.challenges:
            patch_file = challenge.paths.source / Path('patch')

            if patch_file.exists():
                print(str(patch_file))
            else:
                manifest = self.challenge.get_manifest()
                with patch_file.open(mode="w") as pf:
                    patches = manifest.get_patches()
                    json.dump(patches, pf, indent=2)
                    print(patch_file)

    def __str__(self):
        return super().__str__() + "\n"


def gen_polls_args(input_parser):
    pass


patch_parser = add_task("patch", Patch, description='Prints the patch for the challenge.')
gen_polls_args(patch_parser)
