# JackTrip Session Manager

A python tool for automatically handing several clients on a P2P low-latency audio JackTrip connection.

Generates unlimited number of JackTrip server instances as threads, using the python Threading library. Each connection is optimized individually, with automatic connection management and visual status updates for each client's connection quality. This includes information about buffer underruns, overruns, and dropped packets. The manager will attempt to re-connect to clients if any issues arise, which has proven helpful in University network environments. The managing of each individual connection is necessary when conducting large groups of musicians (> 20 individuals,) but is nearly impossible with existing command-line tools, or without hard-coded scripts. JackTrip Session Manager attempts to automate the process of hosting any size JackTrip communication, in order to streamline the process for musicians and educators. 

Jacktrip is an open source, low-latency network performance tool for musicians: https://github.com/jacktrip/jacktrip