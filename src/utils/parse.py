#!/usr/bin/env python3
import re
import os

pid_pattern = r"^# pid (\d{4,7})$"


def kill_process(pid: str, msg: str = None):
    # FIX: find the root cause for this quick fix and implement better solution
    os.system(f"kill {pid}")

    if msg:
        print(msg)


def parse_results(output: str):
    """ Parses out the number of passed and failed tests from cb-test output
    Args:
        output (str): Raw output from running cb-test
    Returns:
        (int, int): # of tests run, # of tests passed
    """

    if 'timed out' in output:
        return None, '3', output, "WARNING: test(s) timed out"

    elif 'not ok - pov did not negotiate' in output:
        return None, '2', output, "WARNING: there was an error running a test"

    # If the test failed to run, consider it failed
    elif 'TOTAL TESTS' not in output:
        for line in output.splitlines():
            match = re.match(pid_pattern, line)
            if match:
                kill_process(match.group(1), f"Killed process {match.group(1)}")

        return None, '2', output, "WARNING: there was an error running a test"

    # Parse out results
    total = output.split('TOTAL TESTS: ')[1].split('\n')[0]
    passed = output.split('TOTAL PASSED: ')[1].split('\n')[0]

    return total, passed, output, None
