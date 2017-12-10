# The Dragons Arena System (DAS)
The DAS is a distributed simulation of a virtual gaming world where players fight against dragons. 
The project was developed in the course *Distributed Systems* lectured by prof. dr. ir. Alexandru Iosup at Vrije Universiteit Amsterdam in Period 2 of the academic year 2017/2018.

## Screenshots
<span><img src="assets/screen-game.png?raw=true" /></span>
<span><img src="assets/screen-console-tool.png?raw=true" /></span>

## Features

### Consistency

### Scalability

### Fault-tolerance

### Load balancing

### Security: byzantine fault-tolerance

## Architecture

## Installation
Clone the project, set up your python3 environment and install necessary modules with pip.
```
$ git clone https://github.com/jonastheis/das.git
$ cd das
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Run with console tool
With the console tool it's a breeze to create several servers or clients on the current machine without visualizer for test purposes. Just start the console tool and type `help` to see all available commands.
Logs for the servers and clients will be created in the `log` directory according to the id of the server/client.

Before starting a server with the tool, please make sure that the ports are available on your system. The console tool creates the first server on port `TCP/UDP 10000` and `TCP 10010`.
The second server will be started at `TCP/UDP 20000` and `TCP 20010`, the third server ... you get the gist. 

```
$ python -m test.console_control
>> help

server.status - prints up/down status of servers and currently active connections/connected clients
server.init {no} - creates {no} servers, the first with map 'test/das_hell.json'
server.start {id} - starts server with {id}
server.kill {id}  - kills server with {id}
server.killall - kills all servers

client.status - prints up/down status of clients and to which server they are connected
client.init {no} - creates {no} clients
client.start {id} - starts client with {id}
client.kill {id} - kills client with {id}
client.killall - kills all clients

help - shows this help
exit - quits the console helper
```

As an example we're going to start 5 servers and 10 clients. Furthermore we'll add one client with visualizer manually in a separate terminal window to see the game in action.
```
$ python -m test.console_control
>> server.init 5
>> client.init 10
# switch to another terminal
$ python -m client.app --vis
# back in the console tool, when the game is over, kill all server processes
>> server.killall
>> exit
```

## Run manually
To run the application manually first a server with an initial map needs to be started. Every server after that has to be started **without** a map.
Multiple servers *can* be started on the same system by assigning different ports on startup.
The server IPs and ports need to be configured in a json config file, see `./test/das_config.json` for an example.
``` 
python -m server.app

# Parameters
--users # provide initial map when starting first server only: e.g. "./test/das_config.json" 
--config ["./test/das_config.json"] # path to config file with server IPs for clients and p2p between servers 
--port [8000] # specifiy the port on which clients try to connect to the server, convention for p2p between servers: port + 10
--vis # starts with visualizer
--log-prefix ["DEFAULT"] # prefix for the log files
--log-level [20] # specify the log level CRITICAL:50, ERROR:40, WARNING:30, INFO:20, DEBUG:10, NOTSET:0
--game-log # no separate game log
```

Clients *can* be started on the same system as well.
```
python -m client.app

# Parameters
--config ["./test/das_config.json"] # path to config file with server IPs for clients and p2p between servers 
--vis # starts with visualizer
--log-prefix ["DEFAULT"] # prefix for the log files
--log-level [20] # specify the log level CRITICAL:50, ERROR:40, WARNING:30, INFO:20, DEBUG:10, NOTSET:0
--malicious # starts as malicious client which sends invalid commands to the server
--game-log # no separate game log
```

## License
This project is licensed under the [Apache Software License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

See [`LICENSE`](LICENSE) for more information.

    Copyright 2017 Kian Peymani, Jonas Theis
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
       http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.