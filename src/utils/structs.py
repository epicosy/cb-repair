from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChallengeStats:
    name: str


@dataclass
class CompileCommand:
    command: str
    file: Path
    dir: Path
