#!/bin/bash

echo "Starting master server @ 7000"
python3.6 -m server.app --users ./test/das_map.json --config ./test/das_config.json --log-prefix master_node --port 7000 &

echo "Starting two slave servers"
python3.6 -m server.app --users ./test/das_map.json --config ./test/das_config.json --log-prefix slave_1 --port 8000 &
python3.6 -m server.app --users ./test/das_map.json --config ./test/das_config.json --log-prefix slave_2 --port 9000 &

sleep 2

for ((i = 1; i <= $1; i++)); do
#    echo "Spawning client number $i"
    python3.6 -m client.app --log-prefix "$i" &
    sleep .5
done

# To keep the vis in the server going
sleep 1000000
#echo "Done. Check log files (tail -f log/server.log)."