#!/usr/bin/env python3

from core.task import Task
from input_parser import add_task


class Catalog(Task):
    def __init__(self, count: bool = False, sanity: bool = False, errors: bool = False, povs: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.sanity = sanity
        self.errors = errors
        self.povs = povs

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
                print_str += f"\n\tOutcomes: {tests}"

                if self.errors:
                    errors = {k: v['error'] for k, v in sanity.items() if 'error' in v}
                    if errors:
                        print_str += f"\n\tErrors: {errors}"

        if self.povs:
            challenge_paths = self.get_challenge_paths(challenge_name)
            source = challenge_paths.source
            povs = [pd.name for pd in source.iterdir() if pd.match("pov*") and pd.is_dir()]
            print_str += f"\n\tPOVs: {povs}"

        print(print_str)

    def __str__(self):
        pass


def catalog_args(input_parser):
    input_parser.add_argument('--count', action='store_true', help='Prints number of challenges.')
    input_parser.add_argument('--sanity', action='store_true', help='Prints the outcome for the challenges tests.')
    input_parser.add_argument('--errors', action='store_true', help='Prints the code for the challenges tests.')
    input_parser.add_argument('--povs', action='store_true', help='Prints the povs for each challenges.')


catalog_parser = add_task("catalog", Catalog, description="List's benchmark challenges.")
catalog_args(catalog_parser)
