#!/usr/bin/env python3

from core.simple_operation import SimpleOperation
from input_parser import add_simple_operation


class Manifest(SimpleOperation):
    def __init__(self, show: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.show = show

    def __call__(self):
        manifest_file = self.challenge.get_manifest_file()

        if self.show:
            with manifest_file.open(mode="r") as m:
                print(m.read())
        else:
            print(str(manifest_file))


def manifest_args(input_parser):
    input_parser.add_argument('--show', action='store_true', help='Flag to print manifest file.')


manifest_parser = add_simple_operation("manifest", Manifest, description="Lists files containing vulnerabilities.")
manifest_args(manifest_parser)
