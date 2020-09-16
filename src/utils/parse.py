#!/usr/bin/env python3
import re
import os

pid_pattern = r"^# pid (\d{4,7})$"


def parse_results(output: str):
    """ Parses out the number of passed and failed tests from cb-test output
    Args:
        output (str): Raw output from running cb-test
    Returns:
        (int, int): # of tests run, # of tests passed
    """
    # TODO: catch this kind of behaviour not ok - pov did not negotiate
    # If the test failed to run, consider it failed
    if 'TOTAL TESTS' not in output:
        print('\nWARNING: there was an error running a test')
        for line in output.splitlines():
            match = re.match(pid_pattern, line)

            if match:
                # FIX: find the root cause for this quick fix and implement better solution
                os.system(f"kill {match.group(1)}")
                print(f"Killed process {match.group(1)}")

        return '2', '2'

    if 'not ok - pov did not negotiate' in output:
        print('\nWARNING: there was an error running a test')
        return '2', '2'

    if 'timed out' in output:
        print('\nWARNING: test(s) timed out')
        return '3', '3'

    # Parse out results
    total = output.split('TOTAL TESTS: ')[1].split('\n')[0]
    passed = output.split('TOTAL PASSED: ')[1].split('\n')[0]

    return total, passed
