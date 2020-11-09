#!/usr/bin/env python3

import re
import pandas

from core.task import Task
from input_parser import add_task


CWE_REGEX = r'CWE-\d{1,4}'


class Score(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        for challenge in self.challenges:
            challenge_paths = self.configs.lib_paths.get_challenge_paths(challenge)

            with challenge_paths.info.open(mode="r") as ci:
                description = ci.read()
                cwes = re.findall(CWE_REGEX, description)
                cwe_scores = pandas.read_pickle(str(self.configs.tools.scores))
                scores = [round(cwe_scores.loc[cwe_scores['cwe_id'] == cwe]['score'].values[0], 3) for cwe in cwes if cwe in list(cwe_scores['cwe_id'])]
                print(sum(scores)/len(scores))

    def __str__(self):
        pass


def score_args(input_parser):
    pass


info_parser = add_task("score", Score, description="Returns CWE score for the challenges.")
score_args(info_parser)
