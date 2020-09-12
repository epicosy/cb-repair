#!/usr/bin/env python3

from base import Base
from input_parser import add_base


class Catalog(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        challenges = self.get_challenges()
        challenges.sort()

        for challenge in challenges:
            print(challenge)

    def __str__(self):
        pass


def catalog_args(input_parser):
    pass


info_parser = add_base("catalog", Catalog, description="List's benchmark challenges.")
catalog_args(info_parser)
