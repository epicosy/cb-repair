#!/usr/bin/env python3

import re
import pandas

from typing import List, AnyStr

from base import Base
from input_parser import add_base


CWE_REGEX = r'CWE-\d{1,4}'


class Score(Base):
    def __init__(self, challenges: List[AnyStr], **kwargs):
        super().__init__(**kwargs)
        self.challenges = challenges

        if not self.challenges:
            self.challenges = self.get_challenges()
            self.challenges.sort()

    def __call__(self):
        for challenge in self.challenges:
            challenge_paths = self.configuration.lib_paths.get_challenge_paths(challenge)

            with challenge_paths.info.open(mode="r") as ci:
                description = ci.read()
                cwes = re.findall(CWE_REGEX, description)
                cwe_scores = pandas.read_pickle(str(self.configuration.tools.scores))
                scores = [round(cwe_scores.loc[cwe_scores['cwe_id'] == cwe]['score'].values[0], 3) for cwe in cwes if cwe in list(cwe_scores['cwe_id'])]
                print(sum(scores)/len(scores))

    def __str__(self):
        pass


def score_args(input_parser):
    input_parser.add_argument('--challenges', type=str, nargs='+', required=False,
                              help='The challenges to be checked.')


info_parser = add_base("score", Score, description="Returns CWE score for the challenges.")
score_args(info_parser)
