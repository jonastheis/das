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
        print('No id/no provided. please try again.')
    return id


class Server(object):
    @staticmethod
    def handle(text):
        if text.startswith('server.init'):
            no = extract_id(text)
            for i in range(1, no+1):
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
                client_connections = 0
                p2p_connections = 0
            else:
                status = 'running'
                # 1 UDP socket, 2 TCP server sockets #### and x.laddr.port == id*1000+10
                active_connections = list(filter(lambda x: x.status == 'ESTABLISHED', server.connections()))
                client_connections = len(list(filter(lambda x: x.laddr.port == id*10000, active_connections)))
                p2p_connections = len(active_connections) - client_connections

            print('Server {}: {}\tp2p: {}, clients: {}'.format(id, status, p2p_connections, client_connections))

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

        arguments = ['python', '-m', 'server.app',
                     '--config', 'test/das_config.json',
                     '--log-prefix', str(id),
                     '--port', str(port)]
        if master_node:
            arguments.extend(['--users', 'test/das_hell.json'])

        print("Starting Server {} with {}".format(id, arguments))

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
            time.sleep(0.5)

    @staticmethod
    def status():
        for id, client in clients.items():
            if client is None:
                status = 'killed'
                connected_to = 0
            else:
                try:
                    status = client.as_dict()['status']
                    connected_to = list(filter(lambda x: x.status == 'ESTABLISHED', client.connections()))[0].raddr.port
                    connected_to = int(connected_to / 10000)
                except Exception as e:
                    connected_to = 0
                    status = 'killed'
                    clients[id] = None
            print('Client {}: {}\tserver: {}'.format(id, status, connected_to))

    @staticmethod
    def kill(id):
        if id == -1:
            return

        if id in clients:
            client = clients[id]
            if client is None:
                return
            try:
                client.kill()
            except:
                pass
        clients[id] = None

    @staticmethod
    def kill_all():
        for client_id in clients:
            Client.kill(client_id)

    @staticmethod
    def start(id):
        if id == -1:
            return

        arguments = ['python', '-m', 'client.app',
                     '--config', 'test/das_config.json',
                     '--log-prefix', str(id)]

        print("Starting Client {} with {}".format(id, arguments))

        proc = subprocess.Popen(arguments)

        clients[id] = psutil.Process(proc.pid)


if __name__ == '__main__':
    while True:
        text = input('>> ')

        if text == 'help':
            print("""
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
