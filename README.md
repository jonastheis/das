# The Dragons Arena System (DAS)
The DAS is a distributed simulation of a virtual gaming world where players fight against dragons. 
The application consists out of distributed, mirrored and authoritative servers and clients (players).
Clients connect to any of the servers and the servers render the game logic in a consistent, synchronized and fault-tolerant manner based on the clients inputs. 

The project was developed in the course *Distributed Systems* lectured by prof. dr. ir. Alexandru Iosup at Vrije Universiteit Amsterdam in Period 2 of the academic year 2017/2018.

A full description of the game, requirements, design and conducted experiments can be found in the [documentation](assets/documentation.pdf) (pdf).

## Screenshots
<div style="text-align:center"><img src="assets/screen-game.png?raw=true" /></div>
<div style="text-align:center"><img src="assets/screen-console-tool.png?raw=true" /></div>

## System Design
In the big picture the application seems to follow the classical client-(authoritative) server model. A client connects to *- in our case –* any server and is ready to play.

However, the server component as a whole is a reliable, mirrored, distributed peer-to-peer system where a client connects to the closest server (lowest latency).
Within this peer-to-peer network the servers share all incoming commands and render the game logic in a synchronized way and broadcast changes to the connected clients. 

<div style="text-align:center"><img src="assets/server-design.png?raw=true" width="500px" /></div>

Each server module is divided into three main components, each performing isolated tasks.
The server component consists of a *Game Engine*, a *Server for clients* and a *Peer-to-Peer server* that other servers can use to establish a connection to. 
The Game engine executes all game commands in an isolated process. It will receive commands from the server using an IPC queue and will put their responses respectively in the *Response Queue*. 
The *Client server* will accept connections from clients and receive their game commands. After being executed by the server, the response status of commands are sent back to the client. 
To be more specific, the executed commands are broadcasted to all clients, so that they can update their game state. 
The *Peer to Peer* component will accept connections from other servers or connect to them. 
It will broadcast all of the commands received by the *Client server* to other peers and put the commands received from other peers in the *Request Queue*. 

### Scalability, Reliability & Availability
The server architecture of our design enables us to deliver multiple valuable traits such as scalability, reliability and availability. 
The servers connect to each other in a peer-to-peer manner. Consequently, there are no *master nodes* in the peer-to-peer system. 
In other words, the architecture of the servers is flat and therefore there are no server bottlenecks. 
The only exception is that at least one of the servers must have the initial map of the dragons in the field. 
Henceforth, any of the servers can leave the cluster and this will not have any significant effect on the other servers. 
Furthermore, we can dynamically increase the number of servers to be able to handle more clients. 
These newly added servers can be turned off after peak workload is passed to save resource consumption. 
Furthermore, the servers will all maintain a list of peer connections and will iteratively send heartbeat messages to them to ensure they are still available. 
These heartbeat messages are also used to exchange meta-data which is used in other aspect of the system. 
A peer is deemed *kicked* if it fails to respond to a configurable number of heartbeat messages. 
The kicked server can later re-join the cluster by sending an *INIT* message to *any* of the active peers. 
This will allow the kicked server to fetch an updated game map and continue to serve clients.

### Load Balancing
The *Client Server* component also provides a simple UDP socket so that clients can ping all servers and then connect to the server who responded the fastest. 
In a simple approach, this usually results connecting to the geographically closest server which does not provide a good load balancing among the servers if there are many users connecting from one region. 
Therefore the servers exchange metadata about how many clients are currently connected to them. 
Based on this data, the average amount of users a server should host is calculated and the ping response time is artificially delayed. 
Thus, clients receive ping responses of less busy servers first and connect to them. 
Furthermore, in a certain interval servers evaluate their currently connected clients to the total amount of clients and kick some clients if there are too many. 
These clients will immediately re-connect to another server, without noticeable interruption of the game.

### Synchronization
To synchronize servers a timebased approach with the Network Time Protocol (NTP) is used. 
This synchronized time is combined with the concept of game-state tics to reach full consistency among servers. 
Game tics are certain iterative points in time in which an accumulated number of commands from clients is executed. 
In other words, all servers will receive different commands from their clients and other servers for an amount of time but *will not execute them immediately*. 
Instead, in a synchronized interval, all of them will execute the commands at once and broadcast the responses to all clients connected to them. 
Two further details elaborate how this approach can be a sophisticated consistency mechanism. 
First, at the beginning of each execution tic, all servers will sort commands based on their timestamp. 
This ensures that all servers will execute the commands in order. 
Secondly, to ensure that commands received by a server actually belong to that specific tic, we prevent servers from executing commands which were received very late within each tic interval. 
Instead these commands are executed in the next tic. In other words, this ensures that no server executes a command before it has been broadcasted to the other servers. 
Thus, it ensures *consistency*. The threshold of postponing messages to the next interval can be configured based on cluster network delay in which the servers are deployed.

### Security: byzantine fault-tolerance
The system is able to cope with arbitrary failures. For example, if a dragon dies while it has plenty of hp or a client moves more than one step (maliciously sent information), the system will be able to cope with this. 
This is achieved by basically whitelisting valid movements within the game on the authoritative server. 

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
