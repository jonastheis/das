#!/usr/bin/env python

# run at least two instances of this program on either same node or multiple
# nodes on local network, along with 'chat_chan_server.py'; text typed in a
# client is broadcast over a channel to all clients

import sys, logging
import pycos.netpycos as pycos

pycos.logger.setLevel(pycos.logger.DEBUG)

channel = None
client_id = None
# this task receives messages from server
def recv_proc(client_id, task=None):
    task.set_daemon()
    while True:
        msg, who = yield task.receive()
        # ignore messages from self (sent by local 'send_proc')
        if who == client_id:
            continue
        print('    %s %s' % (who, msg))


# this task sends messages to channel (to broadcast to all clients)
def send_proc(task=None):
    global channel, client_id
    # if server is in a remote network, use 'peer' as (optionally enabling
    # streaming for efficiency):
    yield pycos.Pycos.instance().peer('127.0.0.1')
    server = yield pycos.Task.locate('game_server')
    channel = yield pycos.Channel.locate('game_channel', server.location)
    recv_task = pycos.Task(recv_proc, client_id)
    yield channel.subscribe(recv_task)

def send_message(msg):
    channel.send((msg, client_id))

def init():
    pycos.Task(send_proc)
