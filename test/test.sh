#!/bin/bash

mkdir test/log

echo "Starting Server..."
script "python3 -m server.network.server &" -f a.log

for ((i = 1; i <= $1; i++)); do
    echo "Spawning client number $i"
    python3 -m test.simple 2>&1> test/log/client_$i.log &
done


echo "Done. Check log files (tail -f log/server.log)."

