#!/usr/bin/env python3

from json import loads
from pathlib import Path
from typing import List
from sys import stderr

from context import Context
from input_parser import add_operation


class Compile(Context):
    def __init__(self,
                 inst_files: List[str] = None,
                 fix_files: List[str] = None,
                 cpp_files: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.commands_path = self.build_root / Path('compile_commands.json')
        self.compile_script = self.working_dir / Path("compile.sh")
        self.inst_files = inst_files
        self.fixes = fix_files
        self.cpp_files = cpp_files

        if self.fixes and not isinstance(self.fixes, list):
            self.fixes = [self.fixes]

        self.log(str(self))

        if self.fixes and self.inst_files and len(self.fixes) != len(self.inst_files):
            raise ValueError(f"The files with changes [{fix_files}] can not be mapped. Uneven number of files " +
                             f"[{inst_files}].")

    def __call__(self):
        self.status(f"Compiling {self.challenge.name}.\n")

        if self.inst_files:
            link_file = self.cmake / Path("link.txt")

            # compile the preprocessed file to object
            with self.commands_path.open(mode="r") as json_file:
                self.compile_commands = loads(json_file.read())

            manifest = self.challenge.get_manifest(self.source)
            mapping = manifest.map_instrumented_files(self.inst_files, cpp_files=self.cpp_files)

            if not mapping:
                self.status(f"Could not map fix files {self.fixes} with source files.\n",
                            file=stderr)
                exit(1)

            # creating object files
            for source_file, cpp_file in mapping.items():

                if self.fixes:
                    cpp_file = self.fixes.pop(0)

                if not Path(cpp_file).exists():
                    self.status(f"File {cpp_file} not found.\n", file=stderr)
                    exit(1)

                compile_command = self.get_compile_command(source_file, cpp_file)
                print(compile_command)
                super().__call__(cmd_str=compile_command,
                                 msg=f"Creating object file for {cpp_file}.\n",
                                 cmd_cwd=str(self.build),
                                 exit_err=True)

            # links objects into executable
            super().__call__(cmd_str=f"cmake -E cmake_link_script {link_file} {self.challenge.name}",
                             msg="Linking object files into executable.\n",
                             cmd_cwd=str(self.build),
                             exit_err=True
                             )
        else:
            super().__call__(cmd_str=f"{self.compile_script} {self.challenge.name}",
                             cmd_cwd=self.working_dir,
                             exit_err=True)

    def get_compile_command(self, manifest_file: str, instrumented_file: str):
        if self.prefix:
            instrumented_file = str(self.prefix / Path(instrumented_file))
        for command_entry in self.compile_commands:
            if command_entry["file"].endswith(manifest_file) and "-DPATCHED" not in command_entry["command"]:
                command = command_entry["command"]
                source_file = command_entry["file"]
                modified_command = command.replace(source_file, instrumented_file)
                modified_command = modified_command.replace('-save-temps=obj', '')

                return modified_command

        self.status(f"Could not find compile command.\n", file=stderr)
        exit(1)

    def __str__(self):
        compile_cmd_str = ""

        if self.inst_files:
            compile_cmd_str += f" --inst_files {' '.join(self.inst_files)}"

        if self.fixes:
            compile_cmd_str += f" --fix_file {self.fixes}"

        return super().__str__() + compile_cmd_str + "\n"


def compile_args(input_parser):
    input_parser.add_argument('-ifs', '--inst_files', nargs='+', help='Instrumented files to compile.', default=None)
    input_parser.add_argument('-cpp', '--cpp_files', action='store_true', required=False,
                              help='Instrumented files are preprocessed.')
    input_parser.add_argument('-ffs', '--fix_files', nargs='+', default=None,
                              help='The file with changes applied by the repair tool.')


c_parser = add_operation("compile", Compile, 'Compiles challenge binary.')
compile_args(c_parser)
