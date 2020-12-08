#!/usr/bin/env python3

from json import loads
from os import environ
from pathlib import Path
from typing import List

from core.operation import Operation
from input_parser import add_operation
from utils.metadata.manifest import map_instrumented_files


class Compile(Operation):
    def __init__(self,
                 inst_files: List[str] = None,
                 fix_files: List[str] = None,
                 cpp_files: bool = False,
                 coverage: bool = False,
                 gcc: bool = False,
                 link: bool = False,
                 exit_err: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.commands_path = self.build_root / Path('compile_commands.json')
        self.compile_script = self.working_dir / Path("compile.sh")
        self.stats = self.working_dir / Path("stats", "compile.txt")
        self.stats.parent.mkdir(parents=True, exist_ok=True)
        self.inst_files = inst_files
        self.fixes = fix_files
        self.cpp_files = cpp_files
        self.exit_err = exit_err
        self.coverage = coverage
        self.gcc = gcc
        self.link = link
        self.link_file = self.cmake / Path("link.txt")

        if self.coverage:
            environ["COVERAGE"] = "True"

        if self.gcc:
            environ["CC"] = "/usr/bin/gcc"
            environ["CXX"] = "/usr/bin/g++"

        self.set_env()

        if self.fixes and not isinstance(self.fixes, list):
            self.fixes = [self.fixes]

        self.log(str(self))

        if self.fixes and self.inst_files and len(self.fixes) != len(self.inst_files):
            self.outcome(1, f"The files with changes [{fix_files}] can not be mapped. Uneven number of files " +
                            f"[{inst_files}].")

    def __call__(self):
        if self.link:
            self.status(f"Linking into executable {self.challenge.name}.")
            self.link_executable()
        elif self.inst_files:
            self.status(f"Compiling preprocessed file for {self.challenge.name}.")
            # compile the preprocessed file to object
            with self.commands_path.open(mode="r") as json_file:
                self.compile_commands = loads(json_file.read())

            mapping = map_instrumented_files(self.inst_files, cpp_files=self.cpp_files,
                                             manifest_path=self.source / Path('manifest'))

            if not mapping:
                self.outcome(1, f"Could not map fix files {self.fixes} with source files.")

            # creating object files
            for source_file, cpp_file in mapping.items():

                if self.fixes:
                    cpp_file = self.fixes.pop(0)

                    if self.prefix:
                        cpp_file = str(self.prefix / Path(cpp_file))

                if not Path(cpp_file).exists():
                    self.outcome(1, f"File {cpp_file} not found.")

                compile_command = self.get_compile_command(source_file, cpp_file)
                out, err = super().__call__(cmd_str=compile_command,
                                            msg=f"Creating object file for {cpp_file}.\n",
                                            cmd_cwd=str(self.build),
                                            exit_err=False)
                if err:
                    self.outcome(1, err)

            # links objects into executable
            self.link_executable()
        else:
            self.status(f"Compiling {self.challenge.name}.")
            out, err = super().__call__(cmd_str=f"{self.compile_script} {self.challenge.name}",
                                        cmd_cwd=self.working_dir,
                                        exit_err=False)

            with (self.source / Path('manifest')).open(mode="r") as mf, self.commands_path.open(mode="r") as json_file:
                self.compile_commands = loads(json_file.read())
                for m in mf.read().splitlines():
                    compile_command = self.get_compile_command(m)
                    cc_split = compile_command.split()
                    cc_split[0] = Path(cc_split[0]).name
                    print(' '.join(cc_split))
            if err:
                self.outcome(1, err)

            self.outcome(0)

#        print(self.build, ' '.join(self.inst_files) if self.inst_files else "")
        self.status(f"Compiled {self.challenge.name}.", ok=True)
        return None, None

    def link_executable(self):
        if not self.link_file.exists():
            self.outcome(1, "No link file found")
        else:
            out, err = super().__call__(cmd_str=f"cmake -E cmake_link_script {self.link_file} {self.challenge.name}",
                                        msg="Linking object files into executable.\n",
                                        cmd_cwd=str(self.build),
                                        exit_err=False)
            if err:
                self.outcome(1, err)
            else:
                self.outcome(0)

    def get_compile_command(self, manifest_file: str, instrumented_file: str = None):
        for command_entry in self.compile_commands:
            if command_entry["file"].endswith(manifest_file) and "-DPATCHED" not in command_entry["command"]:
                command = command_entry["command"]
                source_file = command_entry["file"]
                modified_command = command.replace('-save-temps=obj', '')

                if instrumented_file:
                    modified_command = modified_command.replace(source_file, instrumented_file)

                return modified_command

        self.outcome(1, "Could not find compile command.")

    def outcome(self, result: int, msg: str = None):
        if self.coverage:
            del environ['COVERAGE']
        if self.gcc:
            del environ["CC"]
            del environ["CXX"]

        with self.stats.open(mode="a") as s:
            s.write(f"{result}\n")

            if result == 1:
                self.status(msg, err=True)

                if self.exit_err:
                    exit(1)
                else:
                    return None, msg

    def __str__(self):
        compile_cmd_str = ""

        if self.inst_files:
            compile_cmd_str += f" --inst_files {' '.join(self.inst_files)}"

        if self.fixes:
            compile_cmd_str += f" --fix_file {self.fixes}"

        return super().__str__() + compile_cmd_str + "\n"


def compile_args(input_parser):
    input_parser.add_argument('-ifs', '--inst_files', nargs='+', help='Instrumented files to compile.', default=None)
    input_parser.add_argument('--gcc', action='store_true', help='Uses gcc instead of clang to compile.', default=None)
    input_parser.add_argument('-ee', '--exit_err', action='store_false', required=False,
                              help='Exits when error occurred.')
    input_parser.add_argument('--coverage', action='store_true', required=False, help='Cmake generates gcov files.')
    input_parser.add_argument('--link', action='store_true', required=False,
                              help='Flag for only links objects into executable.')
    input_parser.add_argument('-cpp', '--cpp_files', action='store_true', required=False,
                              help='Flag to indicate that instrumented files are preprocessed.')
    input_parser.add_argument('-ffs', '--fix_files', nargs='+', default=None,
                              help='The file with changes applied by the repair tool.')


c_parser = add_operation("compile", Compile, 'Compiles challenge binary.')
compile_args(c_parser)
