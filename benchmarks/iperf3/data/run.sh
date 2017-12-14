#!/bin/bash

nohup ping -i .5 -w $1 $2 >> pingout.txt &
iperf3 -c $2 -f m --time $1 -J --logfile iperf.json
