#!/usr/bin/env python3

from setting import Setting
from input_parser import add_task


class Manifest(Setting):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        manifest = self.challenge.get_manifest()
        vuln_files = manifest.vuln_files.keys()
        print('\n'.join(vuln_files))


def manifest_args(input_parser):
    pass


info_parser = add_task("manifest", Manifest, description="Lists files containing vulnerabilities.")
manifest_args(info_parser)
