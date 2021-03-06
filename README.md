# JackTrip Session Manager

A python-based GUI for automatically handing several clients on a P2P low-latency audio JackTrip connection.

![Interface Screenshot](Misc/JT-ServerManager-Interface.jpeg)

Generates an unlimited number of JackTrip server instances as threads using the python Threading library. Each connection is optimized individually, with automatic connection management and visual status updates for each client's connection quality. This includes information about buffer underruns, overruns, and dropped packets. The manager will attempt to re-connect to clients if any issues arise, which has proven helpful in University network environments. The managing of each individual connection is necessary when conducting large groups of musicians (> 20 individuals,) but is nearly impossible with existing command-line tools, or without hard-coded scripts. JackTrip Session Manager attempts to automate the process of hosting any size JackTrip communication, in order to streamline the process for musicians and educators. 

## Prerequisites ##
- MacOS or Linux
- Python 3
- Jack https://jackaudio.org/downloads/
- JackTrip https://ccrma.stanford.edu/software/jacktrip/
- Jack running in background, either using qjackctl (GUI provided with Jack) or jackd (command-line)

## Installation ##

- Clone this repo
```bash
git clone https://github.com/carlmoore256/jacktrip-server-manager
cd jacktrip-server-manager
```

- Install dependencies: PySimpleGui
```bash
pip install -r requirements.txt
```

## Using JackTrip Session Manager ##
- Run main.py
```bash
python3 main.py
```

### Saving/Loading Sessions
- Sessions can be saved into a CSV containing the current list of clients and their respective settings. Hit "save session," choose a folder, and enter the filename
- To load a session, select load session and select a previously saved CSV containing the session data

## JackTrip and Jack
JackTrip is an open source, low-latency network performance tool for musicians: https://github.com/jacktrip/jacktrip
Jack Audio Connection Kit is the audio backend for JackTrip: https://github.com/jackaudio/jack2
