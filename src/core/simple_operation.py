#!/usr/bin/env python3

from .kernel import Kernel


class SimpleOperation(Kernel):
    def __init__(self,
                 challenge: str,
                 **kwargs):
        super().__init__(**kwargs)
        self.challenge = self.get_challenge(challenge_name=challenge)

    def __str__(self):
        return super().__str__() + f" -challenge {self.challenge.name}"
