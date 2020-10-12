#!/usr/bin/env python3

import shutil
from pathlib import Path

from setting import Setting
from input_parser import add_task
from distutils.dir_util import copy_tree


class GenPolls(Setting):
    def __init__(self, count: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        assert self.count > 0

    def __call__(self):
        self.status(f"Creating directories for {self.challenge.name} polls.\n")

        poller = self.challenge.paths.poller
        polls_dir = self.challenge.paths.polls

        if polls_dir.exists():
            self.status(f"Deleting existing polls for {self.challenge.name}.\n")
            shutil.rmtree(str(polls_dir))

        polls_dir.mkdir(parents=True, exist_ok=True)

        for poll_dir in poller.iterdir():
            if poll_dir.is_dir():
                self.out_dir = polls_dir / Path(poll_dir.name)
                state_machine_script = poll_dir / Path("machine.py")
                state_graph = poll_dir / Path("state-graph.yaml")

                if state_machine_script.exists() and state_graph.exists():
                    self.out_dir.mkdir(parents=True, exist_ok=True)
                    cmd_str = f"python -B {self.get_tools().gen_polls} --count {self.count} " \
                              f"--store_seed --depth 1048575 {state_machine_script} {state_graph} {self.out_dir}"

                    super().__call__(cmd_str=cmd_str,
                                     msg=f"Generating polls for {self.challenge.name}.\n")
                    break
                elif any(poll_dir.iterdir()):
                    self.status(f"No scripts for generating polls for {self.challenge.name}.\n")
                    self.status(f"Coping pre-generated polls for {self.challenge.name}.\n")
                    self.out_dir.mkdir(parents=True, exist_ok=True)
                    polls = [poll for poll in poll_dir.iterdir() if poll.suffix == ".xml"]
                    polls.sort()
                    polls = polls[:self.count] if len(polls) > self.count else polls
                    for poll in polls:
                        shutil.copy(str(poll), self.out_dir)
                    #copy_tree(src=str(polldir), dst=str(self.out_dir))
                    break

    def __str__(self):
        return super().__str__() + f" -n {self.count}\n"


def gen_polls_args(input_parser):
    input_parser.add_argument('-n', '--count', type=int, default=100,
                              help='Number of traversals through the state graph per round')


info_parser = add_task("genpolls", GenPolls, description='For a given challenge, generates polls which are'
                                                         'deterministic iterations of a non-deterministic state '
                                                         'graph. These are used as positive tests.')
gen_polls_args(info_parser)
