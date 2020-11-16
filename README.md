# cb-repair
An infrastructure that extends a collection of 70 vulnerable programs in C code into a benchmark for automatic program 
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

## Notes

---
* The benchmark was tested on Linux OS with kernel release 5.3.0-64-generic, version #58-Ubuntu SMP and x86_64
architecture.
* The benchmark is supposed to work on other Linux distributions.
* Make sure the scripts ```src/cb-repair.py, src/operations/checkout.py, src/operations/compile.py, 
src/operations/test.py, tools/generate-polls/generate-polls, tools/compile.sh``` are executable.
* To run on Docker, core dumps need to be enabled. 
* Polls generation needs to be performed only once.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Install the necessary dependencies before running the project.

##### Software:
* [Python (2.7)](https://www.python.org/)
    - psutil
* [Python (=>3.7)](https://www.python.org/)

##### Linux Packages:
* libc6-dev libc6-dev-i386 gcc-multilib g++-multilib clang cmake

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

#### 4) Generating polls (Optional)
Generate polls for all challenges by running the script ```genpolls.sh``` 

## From Docker

### Setup

1. First, install Docker ([doc](https://docs.docker.com/)).

2. Then, execute the command to build the image from the Docker file where the project 
has been pre-configured and is ready to be used:

```
docker build --force-rm --tag cb-repair:1.0 .
```

### Execute

To run the project:
```
docker run -it cb-repair:1.0 catalog
```

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

## Challenges
From the 202 original linux working challenges, 70 of them were purposely selected to facilitate the generation of 
their test suite, composed by polls and POVs. Part of the removed CBs require for the generation of polls, the shared 
objects created during the build. During the generation of polls, other CBs have been removed for various 
problematic reasons, which can be found in the file '''gen_polls-result.txt'''. Furthermore, challenges that have 
vulnerabilities spawn across multiple files (header files are included) and challenges that don't have any POVs 
working have been removed as well. 

<table>
<thead>
	<tr>
		<th> Raise error during poll generation (52) </th>
		<th> Multiple files (32) </th>
		<th> POVs not working (56) </th>
	</tr>
</thead>
<tbody>
	<tr>
		<td>
		    <ul>
                <li>3D_Image_Toolkit</li>
                <li>Carbonate</li>
                <li>Charter</li>
                <li>Corinth</li>
                <li>Estadio</li>
                <li>Lazybox</li>
                <li>Material_Temperature_Simulation</li>
                <li>Mixology</li>
                <li>Network_File_System</li>
                <li>Network_Queuing_Simulator</li>
                <li>PTaaS</li>
                <li>REMATCH_2--Mail_Server--Crackaddr</li>
                <li>Recipe_and_Pantry_Manager</li>
                <li>Water_Treatment_Facility_Simulator</li>
                <li>payroll</li>
                <li>Image_Compressor</li>
                <li>RRPN</li>
                <li>Azurad</li>
                <li>LazyCalc</li>
                <li>Pattern_Finder</li>
                <li>Snail_Mail</li>
                <li>Venture_Calculator</li>
                <li>CGC_Hangman_Game</li>
                <li>Pac_for_Edges</li>
                <li>TFTTP</li>
                <li>yolodex</li>
                <li>HeartThrob</li>
                <li>Palindrome</li>
                <li>Tick-A-Tack</li>
                <li>commerce_webscale</li>
                <li>reallystream</li>
                <li>HighFrequencyTradingAlgo</li>
                <li>INSULATR</li>
                <li>NarfAgainShell</li>
                <li>NarfRPN</li>
                <li>Packet_Analyzer</li>
                <li>Parking_Permit_Management_System_PPMS</li>
                <li>String_Storage_and_Retrieval</li>
                <li>TIACA</li>
                <li>UTF-late</li>
                <li>Vector_Graphics_2</li>
                <li>Vector_Graphics_Format</li>
                <li>electronictrading</li>
                <li>matrices_for_sale</li>
                <li>simple_integer_calculator</li>
                <li>Multicast_Chat_Server</li>
                <li>Rejistar</li>
                <li>Sample_Shipgame</li>
                <li>Shipgame</li>
                <li>Multipass2</li>
                <li>Multipass3</li>
                <li>NoHiC</li>
            </ul>
		</td>
		<td>
            <ul>
                <li>ASCII_Content_Server</li>
                <li>Accel</li>
                <li>BIRC</li>
                <li>CGC_Board</li>
                <li>CGC_Image_Parser</li>
                <li>CGC_Planet_Markup_Language_Parser</li>
                <li>COLLIDEOSCOPE</li>
                <li>CableGrind</li>
                <li>Childs_Game</li>
                <li>Cromulence_All_Service</li>
                <li>Dungeon_Master</li>
                <li>FISHYXML</li>
                <li>Game_Night</li>
                <li>H20FlowInc</li>
                <li>KTY_Pretty_Printer</li>
                <li>Kaprica_Script_Interpreter</li>
                <li>Matchmaker</li>
                <li>Music_Store_Client</li>
                <li>Order_Up</li>
                <li>PKK_Steganography</li>
                <li>Packet_Receiver</li>
                <li>REMATCH_1--Hat_Trick--Morris_Worm</li>
                <li>Recipe_Database</li>
                <li>SCUBA_Dive_Logging</li>
                <li>Sorter</li>
                <li>WhackJack</li>
                <li>cyber_blogger</li>
                <li>greeter</li>
                <li>pizza_ordering_system</li>
                <li>simpleOCR</li>
                <li>stack_vm</li>
                <li>university_enrollment</li>
            </ul>
        </td>
		<td>
		    <ul>
                <li>BIRC</li>
                <li>Barcoder</li>
                <li>Bloomy_Sunday</li>
                <li>Board_Game</li>
                <li>CLOUDCOMPUTE</li>
                <li>CNMP</li>
                <li>Character_Statistics</li>
                <li>Checkmate</li>
                <li>Differ</li>
                <li>ECM_TCM_Simulator</li>
                <li>Enslavednode_chat</li>
                <li>EternalPass</li>
                <li>FASTLANE</li>
                <li>FaceMag</li>
                <li>Facilities_Access_Control_System</li>
                <li>FailAV</li>
                <li>Finicky_File_Folder</li>
                <li>Flash_File_System</li>
                <li>Fortress</li>
                <li>GREYMATTER</li>
                <li>Hug_Game</li>
                <li>Kaprica_Go</li>
                <li>Messaging</li>
                <li>Monster_Game</li>
                <li>Mount_Filemore</li>
                <li>Multi_Arena_Pursuit_Simulator</li>
                <li>Multi_User_Calendar</li>
                <li>Network_File_System_v3</li>
                <li>Neural_House</li>
                <li>OTPSim</li>
                <li>OUTLAW</li>
                <li>On_Sale</li>
                <li>One_Amp</li>
                <li>One_Vote</li>
                <li>Order_Up</li>
                <li>Overflow_Parking</li>
                <li>PRU</li>
                <li>Personal_Fitness_Manager</li>
                <li>Query_Calculator</li>
                <li>REMATCH_1--Hat_Trick--Morris_Worm</li>
                <li>REMATCH_3--Address_Resolution_Service--SQL_Slammer</li>
                <li>REMATCH_4--CGCRPC_Server--MS08-067</li>
                <li>REMATCH_5--File_Explorer--LNK_Bug</li>
                <li>REMATCH_6--Secure_Server--Heartbleed</li>
                <li>Secure_Compression</li>
                <li>Shortest_Path_Tree_Calculator</li>
                <li>String_Info_Calculator</li>
                <li>Terrible_Ticket_Tracker</li>
                <li>Thermal_Controller_v2</li>
                <li>User_Manager</li>
                <li>Virtual_Machine</li>
                <li>WhackJack</li>
                <li>anagram_game</li>
                <li>middleout</li>
                <li>tribute</li>
                <li>vFilter</li>
            </ul>
        </td>
	</tr>
</tbody>
</table>

### Challenges with no state machine script

* basic_messaging
* CGC_File_System
* CGC_Video_Format_Parser_and_Viewer
* hawaii_sets
* Message_Service
* Particle_Simulator


### Challenges with POVs removed
The timeout used was 60 seconds and most of the removed POVs did not core.
The remaining POVs were renamed in contiguous order.

| Challenge name           | POVs removed |
|--------------------------|--------------|
| ASL6Parse                | 1,3          |
| Diary_Parser             | 2            |
| FSK_BBS                  | 2,3          |
| Griswold                 | 3            |
| TAINTEDLOVE              | 1            |
| TextSearch               | 2            |
| ValveChecks              | 1            |
| router_simulator         | 2            |

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