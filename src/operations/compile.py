#!/usr/bin/env python3

from json import loads
from pathlib import Path
from typing import List

from operation import Operation
from input_parser import add_operation


class Compile(Operation):
    def __init__(self, name: str,
                 inst_files: List[str],
                 fix_file: str,
                 **kwargs):
        super().__init__(name, **kwargs)
        self._set_build_paths()
        self.commands_path = self.build_root / Path('compile_commands.json')
        self.compile_script = self.working_dir / Path("compile.sh")
        self.inst_files = inst_files
        self.fix = fix_file
        self.log(str(self))

        if self.fix and len(self.inst_files) > 1:
            exit(1)

    def __call__(self):
        self.status(f"Compiling {self.challenge.name}.")

        if self.inst_files:

            link_file = self.cmake / Path("link.txt")

            # compile the preprocessed file to object
            with self.commands_path.open(mode="r") as json_file:
                compile_commands = loads(json_file.read())

            manifest = self.challenge.get_manifest(self.working_dir)
            mapping = manifest.map_instrumented_files(self.inst_files)

            # creating object files
            for source_file, cpp_file in mapping.items():

                if self.fix:
                    cpp_file = self.fix

                compile_command = self.get_compile_command(source_file, cpp_file)

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
        for command_entry in self.compile_commands:
            if command_entry["file"].endswith(manifest_file) and "-DPATCHED" not in command_entry["command"]:
                command = command_entry["command"]
                source_file = command_entry["file"]
                modified_command = command.replace(source_file, instrumented_file)
                modified_command = modified_command.replace('-save-temps=obj', '')

                return modified_command

        return None

    def __str__(self):
        compile_cmd_str = ""

        if self.inst_files:
            compile_cmd_str += f" --inst_files {' '.join(self.inst_files)}"

        if self.fix:
            compile_cmd_str += f" --fix_file {self.fix}"

        return super().__str__() + compile_cmd_str + "\n"


def compile_args(input_parser):
    input_parser.add_argument('-ifs', '--inst_files', nargs='+', help='Instrumented files to compile.', default=None)
    input_parser.add_argument('-ff', '--fix_file', type=str, default=None,
                              help='The file with changes applied by the repair tool.')


c_parser = add_operation("compile", Compile, 'Compiles challenge binary.')
compile_args(c_parser)
