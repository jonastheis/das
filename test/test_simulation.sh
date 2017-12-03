#!/bin/bash

echo "Starting master server @ 7000"

echo "Starting simulation with elapsed time of 30 seconds and reduced number of players"
python3.6 -m simulation.app --elap-time 30 --delayBetweenEvents 1 --gta-file WoWSession_Node_Player_Fixed_Dynamic_reduced.zip --num-slave-servers 3