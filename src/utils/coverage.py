#!/usr/bin/env python3
import fileinput

from pathlib import Path
from typing import NoReturn, List


class Coverage:
    def __init__(self,
                 cov_dir: str,
                 out_dir: str,
                 cov_suffix: str,
                 rename_suffix: str,
                 mode: str = 'a'):
        self.dir = Path(cov_dir) if cov_dir else cov_dir
        self.out_dir = Path(out_dir) if out_dir else out_dir
        self.suffix = cov_suffix
        self.rename = rename_suffix
        self.mode = mode

    def __call__(self) -> NoReturn:
        if self.dir and self.out_dir:
            # copy coverage file generated to coverage dir with respective name

            for file in self.collect_files():
                in_file = self.dir / file
                out_path = self.out_dir / file.parent
                out_file = out_path / Path(file.name)

                if not out_path.exists():
                    out_path.mkdir(parents=True, exist_ok=True)

                if in_file.exists():
                    concat_file = Path(file.stem + self.rename) if self.rename else Path(out_file)
                    concat_file = out_path / concat_file

                    with concat_file.open(mode=self.mode) as fout, fileinput.input(in_file) as fin:
                        for line in fin:
                            fout.write(line)
                    # delete the file generated
                    in_file.unlink()

    def collect_files(self) -> List[Path]:
        coverage_files = []

        def recurse_walk(current: Path, parent: Path, suffix: str):
            for f in current.iterdir():
                if f.is_dir():
                    recurse_walk(f, parent / Path(f.name), suffix)
                elif f.name.endswith(suffix):
                    short_path = parent / Path(f.name)
                    coverage_files.append(short_path)

        for folder in self.dir.iterdir():
            if folder.is_dir():
                recurse_walk(folder, Path(folder.name), self.suffix)

        return coverage_files
