#!/usr/bin/env python3

from utils.challenge import Challenge
from .kernel import Kernel


class SimpleOperation(Kernel):
    def __init__(self,
                 challenge: str,
                 **kwargs):
        super().__init__(**kwargs)
        self.has_challenge(challenge)
        self.is_excluded(challenge)
        challenge_paths = self.configs.lib_paths.get_challenge_paths(challenge)
        self.metadata = self.global_metadata[challenge]
        self.challenge = Challenge(challenge_paths)

    def __str__(self):
        return super().__str__() + f" -challenge {self.challenge.name}"
