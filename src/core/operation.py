#!/usr/bin/env python3

from pathlib import Path

from .simple_operation import SimpleOperation


class Operation(SimpleOperation):
    def __init__(self,
                 working_directory: str,
                 prefix: str = None,
                 **kwargs):
        self.working_dir = Path(working_directory)
        self.prefix = Path(prefix) if prefix else prefix
        self.init_file = self.working_dir / ".init"
        
        if self.init_file.exists():
        	with self.init_file.open(mode="r") as f:
        		challenge = f.read().strip()
        		kwargs["challenge"] = challenge
       	
       	super().__init__(**kwargs)
       	self.source = self.working_dir / Path(self.challenge.name)

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
