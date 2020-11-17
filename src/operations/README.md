# Operations

These operations are used in the cb-repair command-line interface.

## Common Options

These options are common across all operations.

--challenge_name *CHALLENGE_NAME*
:   The challenge name

--working_directory *WORKING_DIRECTORY*
:   The working directory

--verbose
:   Verbose output

--log_file *LOG_FILE*
:   Log file to write the results to

--prefix *PREFIX*
:   Path prefix for extra compile and test files from the unknown arguments

--regex *REGEX*
: File containing the regular expression to parse unknown arguments into known

## Unknown Arguments

All unknown arguments can be parsed into known options by using the option ```--regex``` with a file that contains in 
one line the appropriate regex that attributes a tag with the name of a known argument to the match. 

For example:

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 --regex compile_regex.txt
```

Content of compile_regex.txt file:

``` file
".*\s*(?P<fix_file>\d{5}-file.c)\s*.*"
```

## Checkout
Checks-out a particular challenge.

### Synopsis
cb-repair checkout [-h] [-cn CHALLENGE_NAME] [-v] [-l LOG_FILE] [-wd WORKING_DIRECTORY] [-pf PREFIX] [-r REGEX] [-rp]

### Description
Makes a copy of a particular challenge with the necessary files for compilation to the provided working directory.

### Options

--remove_patches
:   Remove the patches and respective definitions from the source code.

### Example Uses

The following creates a copy of the challenge BitBlaster under ```/tmp/BitBlaster_0``` path with the necessary files for
 compiling.

``` console
$ cb_repair.py checkout -cn BitBlaster -wd /tmp/BitBlaster_0
```

## Compile
Compiles a checked-out challenge.

### Synopsis

cb-repair compile [-h] [-cn CHALLENGE_NAME] [-v] [-l LOG_FILE] [-wd WORKING_DIRECTORY] [-pf PREFIX] [-r REGEX] 
[-ifs INST_FILES [INST_FILES ...]] [-ff FIX_FILE [FIX_FILE ...]]

### Description

This script compiles sources and POVs of a checked-out challenge.

### Options

--inst_files *INST_FILES [INST_FILES ...]*
:   Instrumented files to compile.

--fix_file *FIX_FILE [FIX_FILE ...]*
:   The file with changes applied by the repair tool.

### Example Uses

The following compiles the previous checked out challenge BitBlaster, under ```/tmp/BitBlaster_0``` path.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0
```

The instrumented files can be provided, with the option ```--inst_files```. Those are compiled individually and linked 
to the executable. Give the full path.

For example:
``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 --inst_files /tmp/BitBlaster_0/instrumented/src/main.i
```

Note that the instrumented files need to respect the original name of the files that are instrumented and the path until 
the root folder of the challenge to avoid possible name clashes, as these are mapped to the compile commands generated 
by the build system. In the given example we have the prefix ```/tmp/BitBlaster_0/instrumented/``` which can vary but 
the original file instrumented must maintain the name and the parent folders.

In cases where the instrumented file names can not be changed, the option ```--fix_files``` can be used to circumvent 
that. 
For example: 
``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 --inst_files /tmp/BitBlaster_0/instrumented/src/main.i 
--fix_file 00001.c
```

Note that the changed files still need to be mapped as instrumented files, respecting conditions from the note above 
plus the order must be the same.

## Test
Runs tests on a checked-out and compiled challenge.

### Synopsis
cb-repair test [-h] [-cn CHALLENGE_NAME] [-v] [-l LOG_FILE] [-wd WORKING_DIRECTORY] [-pf PREFIX] [-r REGEX]
[-pt | -nt | -tn TESTS [TESTS ...]] [-of OUT_FILE] [-wf] [-ef] [-pn PORT]


### Description 

This script executes a test or test suite on a checked-out challenge and reports the test cases results. 
It also writes all failing test cases to the file out_file and writes.

### Options
The options ```tests, pos_tests and neg_tests``` are mutually exclusive.

--tests *TESTS [TESTS ...]*
:   Name of the test to be executed.

--pos_tests
:   Run all positive tests against the challenge.

--neg_tests
:Run all negative tests against the challenge.

--out_file *OUT_FILE*
:   The file where tests results are written to.

--write_fail
:   Flag for writing the failed test to the specified out_file.

--exit_fail
:   Flag that makes program exit with error when a test fails.

--port *PORT*
:   The TCP port used for testing the CB. If PORT is not provided, a random port will be used.

### Example Uses

The following tests the previous compiled challenge BitBlaster, under ```/tmp/BitBlaster_0``` path on all tests.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0
```

The following tests the previous compiled challenge BitBlaster, under ```/tmp/BitBlaster_0``` path on all positive tests.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 --pos_tests
```


The following tests the previous compiled challenge BitBlaster, under ```/tmp/BitBlaster_0``` path on p1 test which maps
to the ```GEN_00000_00000.xml``` poll.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 -tn p1
```

The following tests the previous compiled challenge BitBlaster, under ```/tmp/BitBlaster_0``` path on n1 test which maps
to the ```pov_1.pov``` pov.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 -tn n1
```

The following tests p1, n1, and writes to the file ```results.txt``` the tests' results.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 -tn p1 n1 --out_file results.txt
```