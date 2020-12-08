from utils.coverage import Coverage
from input_parser import add_operation
from .test import Test


class TestCoverage(Test):
    def __init__(self, cov_dir: str = None, cov_out_dir: str = None, cov_suffix: str = ".path",
                 rename_suffix: str = ".path", gcov: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.coverage = Coverage(cov_dir if cov_dir else self.cmake, out_dir=cov_out_dir, cov_suffix=cov_suffix,
                                 rename_suffix=rename_suffix)
        self.gcov = gcov

    def __call__(self, *args, **kwargs):
        self.status(f"Running {len(self.tests)} tests.")

        for test in self.tests:
            self._set_test(test)
            self._run_test()
            self.coverage()
            self.gcoverage()
            self._process_result()
            self._process_flags()

    def gcoverage(self):
        if self.gcov:
            for f in self.cmake.iterdir():
                if not f.is_dir():
                    continue

                _, _ = super(Test, self).__call__(cmd_str=f"gcov *.gcno", cmd_cwd=f, exit_err=False)

    def __str__(self):
        cmd_str = " --gcov" if self.gcov else ""

        return super().__str__() + cmd_str


def test_coverage_args(input_parser):
    # Coverage group
    g = input_parser.add_argument_group(title="coverage", description="None")
    g.add_argument('-cd', '--cov_dir', type=str, help='The dir where the coverage files are generated.', default=None)
    g.add_argument('-cod', '--cov_out_dir', type=str, help='The dir where the coverage files are output.', default=None)
    g.add_argument('-cs', '--cov_suffix', type=str, help='The suffix of the coverage files generated.', default=".path")
    g.add_argument('-rs', '--rename_suffix', type=str, default=".path",
                   help='Rename the suffix to a specific one when outputting files')
    input_parser.add_argument('--gcov', action='store_true',
                              help='Flag for running gcov on gcno files from compilation.')


tc_parser = add_operation("test-coverage", TestCoverage,
                          'Runs specified tests and performs coverage against challenge binary.')
test_coverage_args(tc_parser)
