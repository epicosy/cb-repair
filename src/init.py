#!/usr/bin/env python3

import json

from utils.ui.terminal import progress, TermPrint
from config import configuration as configs


if configs.metadata.exists():
    TermPrint.print_bold('Benchmark already initialized')
else:
    metadata = {}
    challenges = configs.lib_paths.get_challenges()
    challenges_count = len(challenges)

    for i, challenge in enumerate(challenges):
        metadata[challenge] = {'excluded': False, "excluded_neg_tests": []}
        progress(i, challenges_count, challenge)
    with configs.metadata.open(mode='w') as mf:
        json.dump(metadata, mf, indent=2)

    TermPrint.print_pass('Benchmark initialized')
