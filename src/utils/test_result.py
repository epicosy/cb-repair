import re

pid_pattern = "# pid (\d{4,7})"
polls_failed_pattern = "# polls failed: (\d{1,4})"
pid_debug_pattern = "# \[DEBUG\] pid: (\d{1,7}), sig: (\d{1,2})"
## total tests failed: 1
codes_error = {
    0: None,
    1: "WARNING: there was an error running a test",
    2: "WARNING: pov did not negotiate",
    3: "WARNING: test(s) timed out",
    4: "WARNING: Unknown behavior",
    5: "WARNING: process received signal ",
    6: "WARNING: polls failed ",
    7: "WARNING: pov should have cored, and did not"
}


class TestResult:
    def __init__(self, result: str, total: int, is_pov: bool, duration: int):
        self.result = result
        self.total = total
        self.is_pov = is_pov
        self.duration = duration
        self.passed = 0
        self.code = None
        self.error = None
        self.pids = []
        self.sig = 0
        self.polls_failed = 0
        self._get_pids_sig()
        self()

    def __call__(self):
        """
            Parses out the number of passed and failed tests from cb-test output
        """

        if 'timed out' in self.result:
            self.code = 3

        elif not self.is_pov and self.polls_failed > 0:
            self.code = 6
            codes_error[self.code] = codes_error[self.code] + str(self.polls_failed) + "\n"

        elif 'not ok - pov did not negotiate' in self.result:
            self.code = 2

        # If the test failed to run, consider it failed
        elif 'TOTAL TESTS' not in self.result:
            self.code = 1

        elif 'TOTAL TESTS: ' in self.result:
            # Parse out results
            self.code = 0
            self.total = int(self.result.split('TOTAL TESTS: ')[1].split('\n')[0])
            self.passed = int(self.result.split('TOTAL PASSED: ')[1].split('\n')[0])

            if self.is_pov:
                self.passed ^= 1

                if self.is_sig() and self.passed:
                    self.passed = 0

                    if 'should have cored, and did not' in self.result:
                        self.code = 7
                    else:
                        self.code = 5
                        codes_error[self.code] = codes_error[self.code] + str(self.sig) + "\n"
        else:
            self.code = 4

        self.error = codes_error[self.code]

    def _get_pids_sig(self):
        match = re.search(pid_debug_pattern, self.result)

        if match:
            self.pids.append(match.group(1))
            self.sig = int(match.group(2))
        else:
            match = re.search(pid_pattern, self.result)
            if match:
                self.pids.append(match.group(1))

        match = re.search(polls_failed_pattern, self.result)

        if match:
            self.polls_failed = int(match.group(1))

    def is_sig(self):
        # checks for the signals SIGSEGV, SIGILL, or SIGBUS
        return self.sig in [4, 7, 11]
