import unittest
from client import game, transport
from server.network import server
import threading, time, multiprocessing


class MockGame():
    def __init__(self):
        pass

def start_server():
    s = server.ThreadedServer(8080)

class NetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Called just once.
        """
        # server_process = multiprocessing.Process(target=start_server)
        # server_process.daemon = True
        # server_process.start()
        # print("Waiting for server to load...")
        # time.sleep(2)
        cls._client = transport.ClientTransport(MockGame(), 8081)

    def test_multi_client(self):
        pass


    def test_packet(self):
        msg = "Some Data That should be returned to me"
        print(11, self._client.send_data(msg))
        

    def test_burst(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()



