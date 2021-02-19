#!/usr/bin/env python3

import shutil
from pathlib import Path

from core.simple_operation import SimpleOperation
from input_parser import add_simple_operation


class GenPolls(SimpleOperation):
    def __init__(self, count: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        assert self.count > 0
        self.poller = self.challenge.paths.poller
        self.polls_dir = self.challenge.paths.polls
        self.out_dir = None
        self.polls = []

    def __call__(self):
        self.status(f"Creating directories for {self.challenge.name} polls.")

        if self.polls_dir.exists():
            self.status(f"Deleting existing polls for {self.challenge.name}.", bold=True)
            shutil.rmtree(str(self.polls_dir))

        self.polls_dir.mkdir(parents=True, exist_ok=True)
        self.state_machine()

        if self.global_metadata[self.challenge.name]['sanity']:
            self.global_metadata[self.challenge.name]['sanity'] = {}
            self.save_metadata()

        if self.output or self.error:
            return self.output, self.error

        self.copy_polls()
        return self.output, self.error

    def state_machine(self):
        # looks for the state machine scripts used for generating polls and runs it
        # otherwise sets the directory with the greatest number of polls

        for poll_dir in self.poller.iterdir():
            if poll_dir.is_dir():
                self.out_dir = self.polls_dir / Path(poll_dir.name)
                state_machine_script = poll_dir / Path("machine.py")
                state_graph = poll_dir / Path("state-graph.yaml")

                if state_machine_script.exists() and state_graph.exists():
                    self.out_dir.mkdir(parents=True, exist_ok=True)

                    cmd_str = f"python -B {self.get_tools().gen_polls} --count {self.count} " \
                              f"--store_seed --depth 1048575 {state_machine_script} {state_graph} {self.out_dir}"

                    super().__call__(cmd_str=cmd_str, msg=f"Generating polls for {self.challenge.name}.\n",
                                     cmd_cwd=str(self.challenge.paths.source))

                    if self.error:
                        self.status(self.error, err=True)
                    self.output = f"Generated polls for {self.challenge.name}."
                    self.status(self.output, ok=True)
                    break

                polls = [poll for poll in poll_dir.iterdir() if poll.suffix == ".xml"]

                if len(polls) > len(self.polls):
                    self.polls = polls

    def copy_polls(self):
        if self.polls:
            self.status(f"No scripts for generating polls for {self.challenge.name}.", warn=True)
            self.status(f"Coping pre-generated polls for {self.challenge.name}.\n", bold=True)

            try:
                self.out_dir.mkdir(parents=True, exist_ok=True)

                if len(self.polls) < self.count:
                    self.status(
                        f"Number of polls available {len(self.polls)} less than the number specified {self.count}",
                        warn=True)

                self.polls.sort()
                polls = self.polls[:self.count] if len(self.polls) > self.count else self.polls

                for poll in polls:
                    shutil.copy(str(poll), self.out_dir)
                self.status(f"Copied polls for {self.challenge.name}.", ok=True)

            except Exception as e:
                self.error = str(e)
                self.status(self.error, err=True)
        else:
            err = f"No pre-generated polls found for {self.challenge.name}."
            self.status(err, err=True)

    def __str__(self):
        return super().__str__() + f" -n {self.count}\n"


def gen_polls_args(input_parser):
    input_parser.add_argument('-n', '--count', type=int, default=100,
                              help='Number of traversals through the state graph per round')


info_parser = add_simple_operation("genpolls", GenPolls, description='For a given challenge, generates polls which are'
                                                         'deterministic iterations of a non-deterministic state '
                                                         'graph. These are used as positive tests.')
gen_polls_args(info_parser)
