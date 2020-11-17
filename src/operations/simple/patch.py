#!/usr/bin/env python3
import json
from pathlib import Path

from core.simple_operation import SimpleOperation
from input_parser import add_simple_operation


class Patch(SimpleOperation):
    def __init__(self, show: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.show = show

    def __call__(self):
        patch_file = self.challenge.paths.source / Path('patch')

        if not patch_file.exists():
            _, manifest = self.challenge.get_manifest(force=True)

            with patch_file.open(mode="w") as pf:
                patches = manifest.get_patches()
                json.dump(patches, pf, indent=2)

        if self.show:
            with patch_file.open(mode="r") as m:
                patches = json.load(m)

            for file, patch in patches.items():
                for line_number, lines in patch.items():
                    for i, line in enumerate(lines):
                        print(file, int(line_number)+i, line.strip())
        else:
            print(patch_file)

    def __str__(self):
        return super().__str__() + "\n"


def patch_args(input_parser):
    input_parser.add_argument('--show', action='store_true', help='Flag to print manifest file.')


patch_parser = add_simple_operation("patch", Patch, description='Prints the patch for the challenge.')
patch_args(patch_parser)
