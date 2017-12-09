# The Dragons Arena System (DAS)
The DAS is a distributed simulation of a virtual gaming world where players fight against dragons. 
The project was developed in the course *Distributed Systems* lectured by prof. dr. ir. Alexandru Iosup at Vrije Universiteit Amsterdam in Period 2 of the academic year 2017/2018.

## Screenshots
<span><img src="assets/screen-game.png?raw=true" /></span>
<span><img src="assets/screen-console-tool.png?raw=true" /></span>

## Architecture

## Features

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
With the console tool it's a breeze to create several servers or clients on the current machine without visualizer for test purposes. Just start the console tool and type help to see all available commands.
Logs for the servers and clients will be created in the `log` directory according to the id of the server/client.

Before starting a server with the tool, please make sure that the ports are available on your system. The console tool creates the first server on port `TCP/UDP 10000` and `TCP 10010`.
The second server will be started at `TCP/UDP 20000` and `TCP 20010`, the third server ... you get the gist. 

```
$ python -m test.console_control
>> help

server.status - prints up/down status of servers
server.init {no} - creates {no} servers, the first with map 'test/das_hell.json'
server.start {id} - starts server with {id}
server.kill {id}  - kills server with {id}
server.killall - kills all servers

client.status - prints up/down status of clients
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


## License
