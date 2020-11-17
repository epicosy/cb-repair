#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
from os.path import dirname, abspath
from pathlib import Path

ROOT_DIR = dirname(dirname(abspath(__file__)))
checks_path = Path(ROOT_DIR, "lib", "checks.json")
challenges_path = Path(ROOT_DIR, "lib", 'challenges')
tools_path = dirname(abspath(__file__))


def failing_neg_tests():
    neg_tests_not_ok = []
    for c in challenges_path.iterdir():
        if c.is_dir():
            povs = [f.name for f in c.iterdir() if f.name.startswith('pov')]
            neg_checks = c / Path('neg_checks.txt')
            if neg_checks.exists():
                with neg_checks.open(mode='r') as nc:
                    nt = nc.read().split()
                    if not nt:
                        neg_tests_not_ok.append(c.name)
                        print(nt, povs, c.name)

    neg_tests_not_ok.sort()

    # with open('povs_not_working.txt', 'w') as pnw:
    #    for t in neg_tests_not_ok:
    #        pnw.write(f"{t}\n")

    return neg_tests_not_ok


# lists the challenges that failed or time-outed for exclusion
def excluded_challenges():
    if checks_path.exists():
        excluded = {}

        with checks_path.open(mode="r") as cp:
            checks = json.loads(cp.read())
            for k, v in checks.items():
                for s, t in v.items():
                    if s == 'passed':
                        if not t:
                            excluded[k] = v
                            break
                        if len([test for test in t if test.startswith('n')]) == 0:
                            print(k)
                            excluded[k] = v
                    elif t:
                        excluded[k] = v
                        break

            return excluded
    return None


# checks if challenge vulnerability is spread across multiple files
def multi_file_challenge(manifest_path: Path):
    with manifest_path.open(mode="r") as mp:
        files = mp.readlines()
        for file in files:
            print(file)
        return len(files) > 1


def excluded_challenges_2():
    tmp_path = Path('/tmp')
    multi_file_challenges = []

    for folder in tmp_path.iterdir():
        if folder.is_dir():
            names = folder.name.split("_")

            if names[0] == "check":
                challenge_name = '_'.join(names[1:])
                manifest_path = folder / Path(challenge_name, 'manifest.txt')

                if multi_file_challenge(manifest_path):
                    multi_file_challenges.append(challenge_name)

    multi_file_challenges.sort()
    excluded = set(multi_file_challenges + failing_neg_tests())
    # with open('excluded.txt', 'w') as ex:
    #    excluded = list(excluded)
    #    excluded.sort()
    #    for e in excluded:
    #        ex.write(f"{e}\n")

    # with open('multi_file_challenges.txt', 'w') as mfc:
    #    for c in multi_file_challenges:
    #        mfc.write(f"{c}\n")

    '''
    for challenge in excluded:
        c_path = challenges_path / Path(challenge)
        if c_path.exists() and c_path.is_dir():
            os.system(f"rm -rf {str(c_path)}")
    '''
    return excluded


def cwe_scores_plot():
    cwe_scores_path = tools_path / Path('cwe_scores.pkl')
    cwe_scores = pd.read_pickle(str(cwe_scores_path))
    cwe_scores['cid'] = cwe_scores.apply(lambda x: int(x['cwe_id'].split('-')[-1]), axis=1)
    cwe_scores.sort_values('cid')
    ax = cwe_scores.plot.scatter(x='cid', y="score", c='DarkBlue')
    #plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         rotation_mode="anchor")
    plt.show()


def unit_tests_results_parsing():
    file = ROOT_DIR / Path('unit_tests_results.txt')
    with file.open(mode="r") as f:
        content = f.read()
        by_challenge = content.split("Challenge: ")
        parsed = {}

        for chal in by_challenge[1:]:
            lines = chal.splitlines()
            splitted = lines[2].split()

            if not int(splitted[1]) > 0:
                continue
            parsed[lines[0]] = ' '.join(splitted).split("AssertionError:")[-1][3:5]

        ordered = list(parsed.keys())
        ordered.sort()
        print(ordered)

unit_tests_results_parsing()
#{'FSK_BBS': 'n2', 'TextSearch': 'n2', 'ASL6parse': 'n1', 'ValveChecks': 'n1', 'router_simulator': 'n2', 'Griswold': 'n3', 'TAINTEDLOVE': 'n1', 'PCM_Message_decoder': 'n1', 'Filesystem_Command_Shell': 'n1', 'Diary_Parser': 'n2'}
