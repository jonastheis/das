#!/bin/bash

mkdir test/log

echo "Starting Server..."
python3.6 -m server.app --users ./test/map.json --vis &

sleep 2

for ((i = 1; i <= $1; i++)); do
#    echo "Spawning client number $i"
    python3.6 -m client.app --log-prefix "$i" &
    sleep .5
done

# To keep the vis in the server going
sleep 1000000
#echo "Done. Check log files (tail -f log/server.log)."

