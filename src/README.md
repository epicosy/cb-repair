# cb-repair
command-line interface to cb-repair.



## Positional Arguments
These are concrete operations and tasks. 
The Operations allow the necessary interactions with the applications — e.g., test a given application. 
The Tasks allow dealing with specific case scenarios — e.g., initialize tests. 
The main difference between operations and tasks is the application's context — i.e., operations make part of an 
execution workflow.

### Operations

    info                Query information about the benchmark challenges.
    genpolls            For a given challenge, generates polls which are deterministic iterations of 
                        a non-deterministic state graph. These are used as positive tests.
    compile             Compiles challenge binary.
    make                Cmake init of the Makefiles.
    checkout            Checks out challenge to working directory.
    test                Runs specified tests against challenge binary.
    test_coverage       Runs specified tests and performs coverage against challenge binary.
    manifest            Lists files containing vulnerabilities.
    patch               Prints the patch for the challenge.

### Tasks
    catalog             List's benchmark challenges.
    clean               Cleans all cache files.
    init_polls          Inits polls for all challenges.
    sanity              Sanity checks for challenges, i.e. runs genpolls (optional), checkout, compile, and test commands
                        as a sanity check, and prints their outcome. Tests' execution can be save as metadata of working tests.
    stats               Statistics about benchmark challenges.

## Common Options

These options are common across all commands.

--excl
:   Flag for not skipping excluded challenges

--verbose
:   Verbose output

--no_status
:   No status output

--log_file *LOG_FILE*
:   Log file to write the results to

### Operations

These options are common across all operations

--working_directory *WORKING_DIRECTORY*
:   The working directory.

--prefix *PREFIX*
:   Path prefix for extra compile and test files for the unknown arguments.

--regex *REGEX*
:   File containing the regular expression to parse unknown arguments into known

### Tasks

These options are common across all tasks

--challenges *CHALLENGES*
:   The targeted challenges.