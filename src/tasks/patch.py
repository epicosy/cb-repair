#!/usr/bin/env python3

from setting import Setting
from input_parser import add_task


class Patch(Setting):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        manifest = self.challenge.get_manifest()
        print(manifest.get_patches(), end='')

    def __str__(self):
        return super().__str__() + "\n"


def gen_polls_args(input_parser):
    pass


patch_parser = add_task("patch", Patch, description='Prints the patch for the challenge.')
gen_polls_args(patch_parser)
