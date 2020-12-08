#!/usr/bin/env python3

import pandas

from core.task import Task
from input_parser import add_task
from utils.parse import cwe_from_info


class Score(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        #cwe_scores = pandas.read_pickle(str(self.configs.tools.scores))
        cwe_scores = pandas.read_csv(str(self.configs.tools.root) + "/scores.csv")
        print(cwe_scores)
        for cn in self.challenges:
            challenge = self.get_challenge(cn)
            main_cwe = challenge.metadata['main_cwe']
            cwes = cwe_from_info(main_cwe)
            scores = [round(cwe_scores.loc[cwe_scores['CWE'] == cwe]['Avg CVSS'].values[0], 3) for cwe in cwes if
                      cwe in list(cwe_scores['CWE'])]
            print(main_cwe, scores)
            #print(sum(scores) / len(scores))

    def __str__(self):
        pass


def score_args(input_parser):
    pass


info_parser = add_task("score", Score, description="Returns CWE score for the challenges.")
score_args(info_parser)
