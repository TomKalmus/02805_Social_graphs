#!/bin/bash

maxdelay=$((59))  # max random value (in seconds)
delay=$(($RANDOM%maxdelay)) # pick an independent random delay
(sleep $((delay)); /usr/bin/python /home/ubuntu/scripts/Test.py # 2>> /home/ubuntu/scripts/logfile.log 1>&2) & # background a subshell to wait, then r$
