#!/usr/bin/env python3

from core.task import Task
from input_parser import add_task


class Catalog(Task):
    def __init__(self, count: bool = False, sanity: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.sanity = sanity

    def __call__(self):
        count = 0
        count_excl = 0

        for challenge in self.challenges:
            if self.excl:
                if self.global_metadata[challenge]['excluded']:
                    count_excl += 1
                    self._print(challenge)
            else:
                count += 1
                self._print(challenge)

        if self.count:
            if self.excl:
                print(count_excl)
            else:
                print(count)

    def _print(self, challenge_name: str):
        sanity = self.global_metadata[challenge_name]['sanity']
        print_str = challenge_name

        if self.sanity:
            if sanity:
                tests = {k: v['outcome'] for k, v in sanity.items()}
                print_str += f"\n\t{tests}"

        print(print_str)

    def __str__(self):
        pass


def catalog_args(input_parser):
    input_parser.add_argument('--count', action='store_true', help='Prints number of challenges.')
    input_parser.add_argument('--sanity', action='store_true', help='Prints the outcome for the challenges tests.')


catalog_parser = add_task("catalog", Catalog, description="List's benchmark challenges.")
catalog_args(catalog_parser)
