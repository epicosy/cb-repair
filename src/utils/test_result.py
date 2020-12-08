import re

pid_pattern = r"^# pid (\d{4,7})$"
pid_debug_pattern = r"^# \[DEBUG\] pid: (\d{1,7}), sig: (\d{1,2})$"

codes_error = {
    0: None,
    1: "WARNING: there was an error running a test",
    2: "WARNING: pov did not negotiate",
    3: "WARNING: test(s) timed out",
    4: "WARNING: Unknown behavior"
}


class TestResult:
    def __init__(self, result: str, total: int, is_pov: bool):
        self.result = result
        self.total = total
        self.is_pov = is_pov
        self.passed = 0
        self.code = None
        self.error = None
        self.pids = []
        self._get_pids()
        self()

    def __call__(self):
        """
            Parses out the number of passed and failed tests from cb-test output
        """

        if 'timed out' in self.result:
            self.code = 3

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
        else:
            self.code = 4

        self.error = codes_error[self.code]

    def _get_pids(self):
        for line in self.result.splitlines():
            match = re.match(pid_debug_pattern, line)
            if match:
                self.pids.append(match.group(1))
            else:
                match = re.match(pid_pattern, line)
                if match:
                    self.pids.append(match.group(1))
