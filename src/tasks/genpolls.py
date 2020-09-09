#!/usr/bin/env python3
from pathlib import Path

from setting import Setting
from input_parser import add_task
from utils.command import Command


class GenPolls(Setting):
    def __init__(self, name: str, count: int, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.count = count
        assert self.count > 0

    def __call__(self):
        self.status(f"Generating polls for {self.challenge.name}.\n")

        poller = self.challenge.paths.poller
        polls_dir = self.challenge.paths.polls
        polls_dir.mkdir(parents=True, exist_ok=True)

        for polldir in poller.iterdir():
            if polldir.is_dir():
                out_dir = polls_dir / Path(polldir.name)
                state_machine_script = polldir / Path("machine.py")
                state_graph = polldir / Path("state-graph.yaml")

                if state_machine_script.exists() and state_graph.exists():
                    out_dir.mkdir(parents=True, exist_ok=True)
                    cmd_str = f"python -B {self.get_tools().gen_polls} --count {self.count} " \
                              f"--store_seed --depth 1048575 {state_machine_script} {state_graph} {out_dir}"
                    cmd = Command(cmd_str)
                    print(cmd_str)
                    _, _ = cmd(verbose=self.verbose, exit_err=False, file=self.log_file)


def gen_polls_args(input_parser):
    input_parser.add_argument('-n', '--count', type=int, default=100,
                              help='Number of traversals through the state graph per round')


info_parser = add_task("genpolls", GenPolls, 'Query information about the benchmark challenges.')
gen_polls_args(info_parser)
