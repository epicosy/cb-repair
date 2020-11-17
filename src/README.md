# cb-repair
command-line interface to cb-repair.

## Positional Arguments

    info                Query information about the benchmark challenges.
    genpolls            For a given challenge, generates polls which are deterministic iterations of 
                        a non-deterministic state graph. These are used as positive tests.
    compile             Compiles challenge binary.
    checkout            Checks out challenge to working directory.
    test                Runs specified test against challenge binary.


## Common Options

These options are common across all operations and tasks.

--challenge_name *CHALLENGE_NAME*
:   The challenge name

--verbose
:   Verbose output

--log_file *LOG_FILE*
:   Log file to write the results to
