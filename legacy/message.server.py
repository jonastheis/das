#!/usr/bin/env python

# chat server; must be used with 'chat_chan_client.py'

import sys, logging
# import netpycos to use distributed version of Pycos
import pycos.netpycos as pycos

# pycos will disconnect if MaxConnectionErrors number of networking errors
# (e.g., conection / send timeout) occur; default is 10
# pycos.MaxConnectionErrors = 3

def server_proc(task=None):
    channel = pycos.Channel('game_channel')
    channel.register()
    task.set_daemon()
    task.register('game_server')

    while True:
        # each message is a 2-tuple
        cmd, who = yield task.receive()
        print(cmd, who)
        channel.send(cmd)

pycos.logger.setLevel(pycos.logger.DEBUG)
server = pycos.Task(server_proc)

while True:
    try:
        cmd = input('Enter "quit" or "exit" to terminate: ').strip().lower()
        if cmd.strip().lower() in ('quit', 'exit'):
            break
    except:
        break

