#!/usr/bin/env python3

from json import loads
from pathlib import Path
from binascii import b2a_hex
from os import urandom

from utils.structs import CompileCommand
from core.operation import Operation
from input_parser import add_operation


class Make(Operation):
    def __init__(self, gcc: bool = False, replace: bool = False, save_temps: bool = False, exit_err: bool = True,
                 compiler_trail_path: bool = False, write_build_args: str = None, no_track: bool = False,
                 sanity_check: bool = False, fault_localization: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.compile_commands = {}
        self.exit_err = exit_err
        self.trail_path = compiler_trail_path
        self.sanity_check = sanity_check
        self.fault_localization = fault_localization
        self.gcc = gcc
        self.no_track = no_track
        self.write_build_args = Path(write_build_args) if write_build_args else None
        self.save_temps = save_temps
        self.replace_ext = "-DCMAKE_CXX_OUTPUT_EXTENSION_REPLACE=ON" if replace else ""
        self._set_cmake_opts()
        self.link_file = self.cmake / Path("link.txt")
        self.cid = b2a_hex(urandom(4)).decode()
        self._set_tracker()

        #self.log(str(self))

    def _set_tracker(self):
        if self.sanity_check and 'sanity_check' not in self.tracker['outcomes']:
            self.tracker['ptr'] = 'sanity_check'
            self.cid = 'sanity_check'
            self.tracker['outcomes']['sanity_check'] = {}
        elif self.fault_localization and 'fault_localization' not in self.tracker['outcomes']:
            self.tracker['ptr'] = 'fault_localization'
            self.cid = 'fault_localization'
            self.tracker['outcomes']['fault_localization'] = {}
        else:
            self.tracker['ptr'] = self.cid
            self.tracker['outcomes'][self.cid] = {}

        if not self.no_track:
            self.save_tracker()

    def _set_cmake_opts(self):
        self.cmake_opts = f"{self.env['CMAKE_OPTS']}" if 'CMAKE_OPTS' in self.env else ""
        self.cmake_opts = f"{self.cmake_opts} -DCMAKE_EXPORT_COMPILE_COMMANDS=ON {self.replace_ext}"

        if self.save_temps:
            self.env["SAVETEMPS"] = "True"

        if self.gcc:
            self.env["CC"] = "gcc"
            self.env["CXX"] = "g++"

        # clang as default compiler
        if "CC" not in self.env:
            self.env["CC"] = "clang"

        if "CXX" not in self.env:
            self.env["CXX"] = "clang++"

        c_compiler = f"-DCMAKE_C_COMPILER={self.env['CC']}"
        asm_compiler = f"-DCMAKE_ASM_COMPILER={self.env['CC']}"
        cxx_compiler = f"-DCMAKE_CXX_COMPILER={self.env['CXX']}"

        # Default shared libs
        build_link = "-DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=OFF"

        if "LINK" in self.env and self.env["LINK"] == "STATIC":
            build_link = "-DBUILD_SHARED_LIBS=OFF -DBUILD_STATIC_LIBS=ON"

        # TODO: Prefer ninja over make, if it is available

        self.cmake_opts = f"{self.cmake_opts} {c_compiler} {asm_compiler} {cxx_compiler} {build_link}"

    def __call__(self):
        self.status("Creating build directory")
        self.build_root.mkdir(exist_ok=True)
        try:
            super().__call__(cmd_str=f"cmake {self.cmake_opts} {self.working_dir} -DCB_PATH:STRING={self.challenge.name}",
                             msg="Creating build files.", cmd_cwd=str(self.build_root))
            if self.error:
                self.outcome(1, self.error)

            self.load_commands()

            if self.write_build_args:
                self._write_build_args()
        finally:
            if self.gcc:
                del self.env["CC"]
                del self.env["CXX"]

            if self.save_temps:
                del self.env["SAVETEMPS"]

    def _write_build_args(self):
        _, manifest = self.challenge.get_manifest(source_path=self.source, force=True)
       
        for fname, _ in {**manifest.source_files, **manifest.vuln_files}.items():
            if fname.endswith(".h"):
                continue
            compile_command = self.compile_commands[fname]

            #if self.include_args:
            #    compile_command.command = f"{compile_command.command} {self.include_args}"

            with self.write_build_args.open(mode="a") as baf:
                cmd = compile_command.command.split()
                bargs = ' '.join(cmd[1:-2])
                baf.write(f"{self.working_dir}\n{bargs}\n")
            
            self.write_build_args.chmod(0o777)

    def load_commands(self):
        if not self.compile_commands:
            compile_commands_file = self.build_root / Path('compile_commands.json')

            with compile_commands_file.open(mode="r") as json_file:
                for entry in loads(json_file.read()):
                    if self.trail_path:
                        entry['command'] = entry['command'].replace('/usr/bin/', '')
                    compile_command = CompileCommand(file=Path(entry['file']), dir=Path(entry['directory']),
                                                     command=entry['command'])
                    if "-DPATCHED" not in compile_command.command:
                        # Looking for the path within the source code folder
                        if str(compile_command.file).startswith(str(self.source)):
                            short_path = compile_command.file.relative_to(self.source)
                        else:
                            short_path = compile_command.file.relative_to(self.working_dir)
                        self.compile_commands[str(short_path)] = compile_command

    def outcome(self, result: int, msg: str = None):
        if self.no_track:
            return None, msg

        if 'compiles' not in self.tracker['outcomes'][self.cid]:
            self.tracker['outcomes'][self.cid]['compiles'] = [result]
        else:
            self.tracker['outcomes'][self.cid]['compiles'].append(result)

        if msg:
            if 'msg' not in self.tracker['outcomes'][self.cid]:
                self.tracker['outcomes'][self.cid]['msg'] = [msg]
            else:
                self.tracker['outcomes'][self.cid]['msg'].append(msg)

        self.save_tracker()

        if result == 1:
            self.status(msg, err=True)

            if self.exit_err:
                exit(1)
            else:
                return None, msg

    def __str__(self):
        make_cmd_str = ""

        if self.gcc:
            make_cmd_str += f" --gcc"

        if self.replace_ext:
            make_cmd_str += f" --replace"

        return super().__str__() + make_cmd_str + "\n"


def make_args(input_parser):
    input_parser.add_argument('--gcc', action='store_true', help='Uses gcc instead of clang to compile.', default=None)
    input_parser.add_argument('--no_track', action='store_true', help='Flag for disabling tracking.', default=None)
    input_parser.add_argument('--write_build_args', type=str, help='File to output build args.', default=None)
    input_parser.add_argument('--compiler_trail_path', action='store_true', help="Trail's compile commands path to compiler")
    input_parser.add_argument('-S', '--save_temps', action='store_true', default=None,
                              help='Store the normally temporary intermediate files.')
    input_parser.add_argument('-ee', '--exit_err', action='store_false', required=False,
                              help='Exits when error occurred.')
    input_parser.add_argument('--replace', action='store_true', help='Replaces output extension.')
    input_parser.add_argument('-sc', '--sanity_check', action='store_true', required=False,
                              help='Flag for tracking sanity check.')
    input_parser.add_argument('-fl', '--fault_localization', action='store_true', required=False,
                              help='Flag for tracking fault localization.')


parser = add_operation("make", Make, 'Cmake init of the Makefiles.')
make_args(parser)
