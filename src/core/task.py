#!/usr/bin/env python3
from typing import List, AnyStr

from .kernel import Kernel


class Task(Kernel):
    def __init__(self, challenges: List[AnyStr], **kwargs):
        super().__init__(**kwargs)
        # self.consider_excluded = consider_excluded

        if challenges:
            for challenge in challenges:
                self.has_challenge(challenge)
                if not self.excl:
                    self.is_excluded(challenge)

            self.challenges = challenges
            self.challenges.sort()

    def __str__(self):
        return super().__str__()
