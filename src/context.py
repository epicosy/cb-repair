#!/usr/bin/env python3

from pathlib import Path

from setting import Setting


class Context(Setting):
    def __init__(self,
                 working_directory: str,
                 prefix: str = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.working_dir = Path(working_directory)
        self.source = self.working_dir / Path(self.challenge.name)
        self.prefix = Path(prefix) if prefix else prefix

    def add_prefix(self, file: Path):
        if self.prefix:
            return self.prefix / file
        return file

    def _set_build_paths(self):
        self.build_root = self.working_dir / Path("build")
        self.build = self.build_root / Path(self.challenge.name)
        self.cmake = self.build / Path("CMakeFiles", f"{self.challenge.name}.dir")

    def __str__(self):
        prefix_cmd = (f' -pf ' + self.prefix) if self.prefix is not None else ""
        return f"{self.name} -wd {self.working_dir} -cn {self.challenge.name}" + prefix_cmd
