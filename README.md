# cb-repair
An infrastructure that extends a collection of 57 vulnerable programs in C code into a benchmark for automatic program 
repair tools. The programs were selected out of 250 applications initially designed for DARPA's Cyber Grand Challenge 
(CGC). 

The applications were purposely built to challenge vulnerability identification and remediation systems, known as 
Challenge Binaries (CB). The CBs were developed for DECREE OS, a custom Linux-derived OS, and subsequently, most of 
the CBs were modified by Trail of Bits to work on Linux, OS X, and Windows. This repository is an extension over 
Trail of Bits' work. 

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


## Table of Contents

* [Repository structure](#repository-structure)
* [Notes](#notes)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
     * [Software](#software)
     * [Linux Packages](#linux-packages)
  * [Setup](#setup)
  * [From Docker](#from-docker)
     * [Build](#build)
     * [Execute](#execute)
* [Usage](#usage)
    * [Baseline](#baseline)
        * [Generating Polls](#generating-polls)
        * [Checkout](#checkout)
        * [Compile](#compile)
        * [Test](#test)
* [Challenges](#challenges)
    * [Descriptive Statistics](#descriptive-statistics)
* [Metadata and Polls](#metadata-and-polls)    
* [Roadmap](#Roadmap)
* [Authors](#Authors)
* [License](#license)
* [Contact](#contact)

## Repository structure

This repository is structured as follows:

```
├── lib: contains the programs along with the include folder that contains their CGC dependencies
├── plots: contains the descriptive plots generated by the stats command
├── src: contains the main scripts to run cb-repair along with its source code
│ ├── Main files:
│ ├── config.py: contains the parameters of cb-repair, e.g. tests' execution timeout, cores path, etc.
│ ├── cb-repair.py: main script to run cb-repair's commands
│ └── init.py: script used to initialize the benchmark's programs, i.e. creates metadata file along with the manifest/patch files.
├── tools: contains original Python scripts used by cb-repair to modify, build, and test the original challenges.
├── Dockerfile: dockerfile to instantiate and run cb-repair on docker
├── gen_polls-result.txt: file with the outcome from running the original cb-multios genpolls.sh script, categorized by error
├── init.sh: script used to download and install dependencies and initialize the benchmark
├── STATS.MD: contains the descriptive statistics along with plots on excluded and selected challenges
├── study_tests.tar.gz: instantiation of sanity check for all challenges
├── python2_requirements.txt: file with requirements for python 2
├── python3_requirements.txt: file with requirements for python 3
```

## Notes

---
* The benchmark was tested on Linux OS with kernel release 5.3.0-64-generic, version #58-Ubuntu SMP and x86_64
architecture.
* The benchmark is supposed to work on other Linux distributions.
* Make sure the scripts ```src/cb-repair.py, tools/generate-polls/generate-polls``` are executable.
* To run on Docker, core dumps need to be enabled. 
* Polls generation needs to be performed only once.
* The default ```cores path``` is ```/cores```, make sure the folder exists with the right permissions.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Install the necessary dependencies and packages before running the project.

##### Software:
* [Python (2.7)](https://www.python.org/)
    - XlsxWriter==1.2.9
    - defusedxml==0.6.0
    - matplotlib==2.2.5
    - numpy==1.16.6
    - pycrypto==2.6.1
    - PyYAML==5.1.2
* [Python (>=3.7)](https://www.python.org/)
    - matplotlib==3.3.3
    - pandas==1.1.4
    - numpy==1.19.4
    - psutil==5.7.3
    - filelock==3.0.12
    
##### Install Linux Packages:
```
sudo apt get install -y libc6-dev libc6-dev-i386 gdb python-dev python3-dev gcc-multilib g++-multilib clang cmake
```
### Setup

This section gives the steps, explanations and examples for getting the project running.

#### 1) Clone this repo

``` console
$ git clone https://github.com/epicosy/cb-repair.git
```

#### 2) Install Prerequisites and initialize benchmark

Run the ```init.sh``` script in the root folder.

#### 3) Configure the project (Optional)
In case you find necessary, some configurations can be changed in the ```src/config.py``` script.
For example, you might want to change the default ```tests_timeout``` or the ```margin``` of the timeouts in case the 
tests were initialized during sanity check. 

### From Docker

#### Build

1. First, install Docker ([doc](https://docs.docker.com/)).

2. Then, execute the command to build the image from the Docker file where the project has been pre-configured and is 
ready to be used:

```
docker build --force-rm --tag cb-repair .
```

#### Enabling core dumps 
On Ubuntu the core dumps are redirected to the standard input of the Apport program, which writes them to the location 
where the crashing app was launched. When running the benchmark with Docker image, core dumps need to be stored on 
specific disk location (by default containers can not write to the file system locations which Apport requires). 

The following is the simplest solution to enable core dumps for Docker containers:

Set the cores generation to the folder ```/cores``` in the host with the specific pattern ```core.pid.path```.
```
echo '/cores/core.%p.%E' | sudo tee /proc/sys/kernel/core_pattern
```
To reset the pattern to the default execute:
```
sudo service apport restart
```

#### Execute
The WORKDIR is ```/cb-repair``` and the main script is ```cb-repair.py```, in the folder ```src```.
Run the container with and query the benchmark with commands, for example: 
```
docker run -it cb-repair 
root@docker_container:/cb-repair# src/cb_repair.py check --challenges BitBlaster --genpolls --count 10 --timeout 10 -v
```

## Usage

The normal usage is, given a challenge, to checkout the challenge, compile and test. For testing you have to make sure
that polls — i.e. positive tests — are initialized for the challenge under test.
Each step is dependent on the previous and for testing the polls must be already generated. POVs — i.e. negative tests — 
are instantiated during compilation.

### Baseline 

This following explains the baseline usage. For more advanced usages check the readme under operations.

#### Generating Polls
This step must be executed at least once, and before testing, as it instantiates the polls.

You can do it per challenge by executing the following:
``` console
$ ./src/cb_repair.py genpolls -cn BitBlaster -n 50 
```

The default number of traversals through the state graph per round is 100. That will generate 100 polls, it can be 
changed by supplying the ```-n``` option followed by the respective number of traversals.

Or all at once, by executing the following:

``` console
$ cb_repair.py init_polls --count 50 
```
For this command, the default number of traversals through the state graph per round is 10.

The generated polls are stored in the folder: ```cb-repair/lib/polls```.

---
Note: It may happen the generation to raise an "AssertionError: node 'node_name' was never executed" for a challenge. 
This is just warning that the state machine did not reach that node during the generation of polls. 
Just raise the number of polls to be generated or re-generate the polls. Same for 'AssertionError: Edge 'edge_name' 
was not traversed".
---

#### Checkout
This command clones a specified challenge under a specified folder.
The following creates a copy of the challenge BitBlaster under ```/tmp/BitBlaster_0``` path with the necessary files for
 compiling.

``` console
$ cb_repair.py checkout -cn BitBlaster -wd /tmp/BitBlaster_0
```

#### Compile 
This command compiles a specified checked out.
The following compiles the previous checked out challenge BitBlaster, under ```/tmp/BitBlaster_0``` path.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0
```

#### Test
This command tests a specified checked out and compiles challenge.
The following tests the previous compiled challenge BitBlaster, under ```/tmp/BitBlaster_0``` path on the positive tests
```p1 p5 p9``` and negative test ```n1```.

``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 -tn p1 p5 p9 n1
```
Also you can execute all the generated positive tests with the flag ```pos_tests```, same for the negative tests, with 
the flag ```--neg_tests```
``` console
$ cb_repair.py compile -cn BitBlaster -wd /tmp/BitBlaster_0 --pos_tests
```

## Challenges
From the 202 original linux working challenges, 57 of them were purposely selected to facilitate the generation of 
their test suite, composed by polls and POVs. Part of the removed CBs require for the generation of polls, the shared 
objects created during the build. During the generation of polls, other CBs have been removed for various 
problematic reasons, which can be found in the file ```gen_polls-result.txt```. Furthermore, challenges that have 
vulnerabilities spawn across multiple files (header files are included) and challenges that don't have any POVs 
working have been removed as well. 

### Descriptive Statistics
You can check the descriptive statistics of the selected challenges [here](STATS.md).

The following are challenges with no state machine script, and generating polls for these, might not fulfill the 
specified number. These come with a certain number of instantiated polls.  A warning message will be raised during polls 
generation in that case.

* basic_messaging
* CGC_File_System
* CGC_Video_Format_Parser_and_Viewer
* hawaii_sets
* Message_Service
* Particle_Simulator

## Metadata and Polls
The compressed file ```study_tests.tar.gz``` contains a version of 20 polls for all challenges. It also contains their 
respective metadata that passed the sanity check. Uncompress the file and copy the ```polls```folder  and ```metadata```
file in the ```libs``` folder of the project. The metadata contains information such as the tests' outcome,
their execution duration, if challenges should be excluded, and the main common CWE.

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