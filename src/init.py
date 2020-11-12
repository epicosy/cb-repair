#!/usr/bin/env python3

import json

from utils.ui.terminal import progress, TermPrint
from config import configuration as configs
from utils.challenge import Challenge

if configs.metadata.exists():
    TermPrint.print_bold('Benchmark already initialized')
else:
    metadata = {}
    challenges = configs.lib_paths.get_challenges()
    challenges_count = len(challenges)

    for i, challenge_name in enumerate(challenges):
        challenge_paths = configs.lib_paths.get_challenge_paths(challenge_name)
        challenge = Challenge(challenge_paths)
        _, manifest = challenge.get_manifest()
        metadata[challenge_name] = {'excluded': False, "excluded_neg_tests": [], 'lines': manifest.total_lines,
                                    'vuln_lines': manifest.vuln_lines, 'patch_lines': manifest.patch_lines}
        progress(i, challenges_count, challenge_name)
    with configs.metadata.open(mode='w') as mf:
        json.dump(metadata, mf, indent=2)

    TermPrint.print_pass('Benchmark initialized')
