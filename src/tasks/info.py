#!/usr/bin/env python3

from setting import Setting
from input_parser import add_task


class Info(Setting):
    def __init__(self, task: str, **kwargs):
        super().__init__(**kwargs)
        self.task = task

    def __call__(self):
        if self.task == "manifest":
            self._manifest()
        elif self.task == "remove_patch":
            self._manifest(remove=True)
        else:
            print(self.challenge.info())

    def _manifest(self, remove: bool = None):
        manifest = self.challenge.get_manifest()

        if remove:
            manifest.remove_patches()

        manifest.write()


def info_args(input_parser):
    input_parser.add_argument('-t', '--task', help='Info related task to be executed.',
                              choices=["manifest", "remove_patch"], type=str, default=None)


info_parser = add_task("info", Info, 'Query information about the benchmark challenges.')
info_args(info_parser)
