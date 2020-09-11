# cb-repair
An infrastructure that extends a collection of 154 vulnerable programs in C code into a benchmark for automatic program 
repair tools. The programs were selected out of 250 applications initially designed for DARPA's Cyber Grand Challenge 
(CGC). 

The applications were purposely built to challenge vulnerability identification and remediation systems, known as 
Challenge Binaries (CB). The CBs were developed for DECREE OS, a custom Linux-derived OS, and subsequently, most of 
the CBs were modified by Trail of Bits to work on Linux, OS X, and Windows. This repository is an extension over 
Trail of Bits' work. The CBs were purposely selected to facilitate the generation of their test suite, composed by polls 
and POVs (part of CBs require the shared objects created during the build in order to generate the polls). 

The infrastructure extends the provided tools and build system, and was designed to make the CBs compatible and 
reproducible for comparative studies and research techniques in automatic patch generation. The similar available 
[benchmarks](http://program-repair.org/benchmarks.html) cover a wide class of defects and permit the evaluation of 
automatic repair tools. 

This benchmark contains programs designed specifically to cover vulnerabilities. The programs approximate real 
software with enough complexity, representing a wide variety of crashing software flaws. Beside the bond for 
compatibility, reproducibility and evaluation, the previous work that the benchmark brings, enables extensive 
functionality testing, significant amount of triggers for introduced bugs, patches, and performance monitoring tools. 
All of that gives the possibility to broadly extend the benchmark with potential use cases that surpass the scope 
of this work. 
 
More about [CGC corpus](http://www.lungetech.com/cgc-corpus/about/), 
[CGC repository](https://github.com/CyberGrandChallenge) and 
[Trail of Bits' cb-multios](https://github.com/trailofbits/cb-multios). 

## Notes

---
* The benchmark was tested on Linux OS with kernel release 5.3.0-64-generic, version #58-Ubuntu SMP and x86_64
architecture.
* The benchmark is supposed to work on other Linux distributions.
* Make sure the scripts ```src/cb-repair.py, src/operations/checkout.py, src/operations/compile.py, 
src/operations/test.py, tools/generate-polls/generate-polls, tools/compile.sh``` are executable.
* To run on Docker, core dumps need to be enabled. 
* Polls generation needs to be performed only once.
* Some positive tests timeout with 10 seconds limit. A check for that will be added.
* Some negative tests don't core. A check for that will be added.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Install the necessary dependencies before running the project.

##### Software:
* [Python (2.7)](https://www.python.org/)
* [Python (=>3.7)](https://www.python.org/)

##### Linux Packages:
* libc6-dev libc6-dev-i386 gcc-multilib g++-multilib clang cmake

### Setup

This section gives the steps, explanations and examples for getting the project running.

#### 1) Clone this repo

``` console
$ git clone https://github.com/epicosy/cb-repair.git
```

#### 2) Install Prerequisites

Run the ```init.sh``` script in the root folder.

#### 3) Configure the project
In case you find necessary, some configurations can be changed in the ```src/config.py``` script.

#### 4) Generating polls (Optional)
Generate polls for all challenges by running the script ```genpolls.sh``` 


## Usage

The normal usage is, given a challenge, to checkout the challenge, compile and test.
Each step is dependent on the previous and for testing the polls must be already generated. POVs are generated during 
compilation.

### Baseline 

This following explains the baseline usage. For more advanced usages check the readme under operations.

#### Generating Polls
This step can be skipped if polls were generated in the setup.

The default number of traversals through the state graph per round is 100. That will generate 100 polls, it can be 
changed by supplying the ```-n``` option followed by the respective number of traversals.

For example, the following will generate 50 polls for BitBlaster challenge. Those are stored under 
```/lib/polls/BitBlaster```.

``` console
$ cb_repair.py genpolls -cn BitBlaster -n 50 
```

#### Checkout
The following creates a copy of the challenge BitBlaster under ```/tmp/BitBlaster_0``` path with the necessary files for
 compiling.

``` console
$ cb_repair.py checkout -cn BitBlaster -wd /tmp/BitBlaster_0
```

#### Compile 
The following compiles the previous checked out challenge BitBlaster, under ```/tmp/BitBlaster_0``` path.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0
```

#### Test

The following tests the previous compiled challenge BitBlaster, under ```/tmp/BitBlaster_0``` path on the positive tests
```p1 p5 p9``` and negative test ```n1```.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 -tn p1 p5 p9 n1
```

## Roadmap

See the [open issues](https://github.com/epicosy/cb-repair/issues) for a list of proposed features (and known issues).


## Authors
Porting work was completed by Kareem El-Faramawi and Loren Maggiore, with help from Artem Dinaburg, Peter Goodman, 
Ryan Stortz, and Jay Little. Challenges were originally created by NARF Industries, Kaprica Security, Chris Eagle, 
Lunge Technology, Cromulence, West Point Military Academy, Thought Networks, and Air Force Research Labs while under 
contract for the DARPA Cyber Grand Challenge.

## License
Distributed under the MIT License. See LICENSE for more information.

## Contact

Eduard Pinconschi - eduard.pinconschi@tecnico.ulisboa.pt