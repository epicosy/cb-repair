#!/usr/bin/env python3
import json
from pathlib import Path

from .simple_operation import SimpleOperation


class Operation(SimpleOperation):
    def __init__(self,
                 working_directory: str,
                 prefix: str = None,
                 **kwargs):
        self.working_dir = Path(working_directory)
        self.prefix = Path(prefix) if prefix else prefix
        self.tracker_file = self.working_dir / ".tracker"
        self._load_tracker()
        kwargs["challenge"] = self.tracker['name']

        super().__init__(**kwargs)
        self.source = self.working_dir / Path(self.challenge.name)

    def _load_tracker(self):
        with self.tracker_file.open(mode="r") as tf:
            self.tracker = json.load(tf)

    def save_tracker(self):
        with self.tracker_file.open(mode="w") as tf:
            json.dump(self.tracker, tf, indent=2)

    def add_prefix(self, file: Path):
        if self.prefix:
            return self.prefix / file
        return file

    def _set_build_paths(self):
        self.build_root = self.working_dir / Path("build")
        self.build = self.build_root / Path(self.challenge.name)
        self.cmake = self.build / Path("CMakeFiles", f"{self.challenge.name}.dir")

    def __str__(self):
        prefix_cmd = f' -pf  {self.prefix}' if self.prefix is not None else ""
        return super().__str__() + f" -wd {self.working_dir} -cn {self.challenge.name}" + prefix_cmd
