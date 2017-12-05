import subprocess
import sys
import os
import psutil
import time

servers = {}
clients = {}


fileDir = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(fileDir)

def extract_id(text):
    id = -1
    try:
        id = int(text.split(' ')[1])
    except:
        print('No id provided. please try again.')
    return id


class Server(object):
    @staticmethod
    def handle(text):
        if text == 'server.init':
            for i in range(1, 6):
                if i == 1:
                    Server.start(i, master_node=True)
                else:
                    Server.start(i)
                time.sleep(0.3)
        elif text == 'server.status':
            Server.status()
        elif text == 'server.killall':
            Server.kill_all()
        elif text.startswith('server.kill'):
            Server.kill(extract_id(text))
        elif text.startswith('server.start'):
            Server.start(extract_id(text))
        else:
            print('Unknown command, type help to see all available commands.')

    @staticmethod
    def status():
        for id, server in servers.items():
            if server is None:
                status = 'killed'
            else:
                status = 'running'
            print('Server {}: {}'.format(id, status))

    @staticmethod
    def kill(id):
        if id == -1:
            return

        if id in servers:
            server = servers[id]
            if server is None:
                return
            for child in server.children():
                child.kill()
            server.kill()
        servers[id] = None

    @staticmethod
    def kill_all():
        for server_id in servers:
            Server.kill(server_id)

    @staticmethod
    def start(id, master_node=False):
        if id == -1:
            return

        port = id * 10000

        arguments = ['python3.6', '-m', 'server.app',
                     '--config', 'test/das_config_console_control.json',
                     '--log-prefix', str(id),
                     '--port', str(port)]
        if master_node:
            arguments.extend(['--users', 'test/das_map.json'])

        proc = subprocess.Popen(arguments)

        servers[id] = psutil.Process(proc.pid)


class Client(object):
    @staticmethod
    def handle(text):
        if text == 'client.status':
            Client.status()
        elif text == 'client.killall':
            Client.kill_all()
        elif text.startswith('client.init'):
            Client.create(extract_id(text))
        elif text.startswith('client.kill'):
            Client.kill(extract_id(text))
        elif text.startswith('client.start'):
            Client.start(extract_id(text))
        else:
            print('Unknown command, type help to see all available commands.')

    @staticmethod
    def create(count):
        for i in range(1, count+1):
            Client.start(i)
            time.sleep(0.1)

    @staticmethod
    def status():
        for id, client in clients.items():
            if client is None:
                status = 'killed'
            else:
                try:
                    status = client.as_dict()['status']
                    if status == 'zombie':
                        status = 'killed'
                except:
                    status = 'killed'
                    clients[id] = None
            print('Client {}: {}'.format(id, status))

    @staticmethod
    def kill(id):
        if id == -1:
            return

        if id in clients:
            client = clients[id]
            if client is None:
                return
            client.kill()
        clients[id] = None

    @staticmethod
    def kill_all():
        for client_id in clients:
            Client.kill(client_id)

    @staticmethod
    def start(id):
        if id == -1:
            return

        arguments = ['python3.6', '-m', 'client.app',
                     '--config', 'test/das_config_console_control.json',
                     '--log-prefix', str(id)]

        proc = subprocess.Popen(arguments)

        clients[id] = psutil.Process(proc.pid)


if __name__ == '__main__':
    while True:
        text = input('>> ')

        if text == 'help':
            print("""
server.status - prints up/down status of servers
server.init - spawns 5 servers
server.start {id} - starts server with {id}
server.kill {id}  - kills server with {id}
server.killall - kills all servers

client.status - prints up/down status of clients
client.create {no} - creates {no} clients
client.start {id} - starts client with {id}
client.kill {id} - kills client with {id}
client.killall - kills all clients

help - shows this help
exit - quits the console helper
            """)
        elif text == 'exit':
            Client.kill_all()
            Server.kill_all()
            break
        elif text.startswith('server'):
            Server.handle(text)
        elif text.startswith('client'):
            Client.handle(text)
        else:
            print('Unknown command, type help to see all available commands.')




#proc = subprocess.Popen([sys.executable, clientApp, '--log-prefix', event_details.playerId])

