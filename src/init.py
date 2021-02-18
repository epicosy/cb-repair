#!/usr/bin/env python3

import json
from pathlib import Path

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
        challenge = Challenge(challenge_paths, {})
        main_cwe = challenge.cwe_type()
        _, manifest = challenge.get_manifest(force=True)
        patch_file = challenge.paths.source / Path('patch')

        with patch_file.open(mode="w") as pf:
            patches = manifest.get_patches()
            json.dump(patches, pf, indent=2)

        metadata[challenge_name] = {'excluded': False, 'lines': manifest.total_lines,
                                    'vuln_lines': manifest.vuln_lines, 'patch_lines': manifest.patch_lines,
                                    'vuln_files': len(manifest.vuln_files), 'main_cwe': main_cwe,
                                    'sanity': {}}

        progress(i, challenges_count, challenge_name)

        with configs.metadata.open(mode='w') as mf:
            json.dump(metadata, mf, indent=2)

    TermPrint.print_pass('Benchmark initialized')
