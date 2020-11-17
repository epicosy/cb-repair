#!/usr/bin/env python3

import pandas

from core.task import Task
from input_parser import add_task
from utils.parse import cwe_from_info


class Score(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        cwe_scores = pandas.read_pickle(str(self.configs.tools.scores))
        for challenge in self.challenges:
            challenge_paths = self.configs.lib_paths.get_challenge_paths(challenge)

            with challenge_paths.info.open(mode="r") as ci:
                description = ci.read()
                cwes = cwe_from_info(description)
                scores = [round(cwe_scores.loc[cwe_scores['cwe_id'] == cwe]['score'].values[0], 3) for cwe in cwes if cwe in list(cwe_scores['cwe_id'])]
                print(sum(scores)/len(scores))

    def __str__(self):
        pass


def score_args(input_parser):
    pass


info_parser = add_task("score", Score, description="Returns CWE score for the challenges.")
score_args(info_parser)
