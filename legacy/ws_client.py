import websocket
import threading

class NetworkClient():
    def __init__(self, game):
        self.game = game

        def on_message(ws, message):
            print(message)

        def on_error(ws, error):
            print "ERRRR"
            print(error)

        def on_close(ws):
            print ws
            print("### closed ###")

        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://localhost:8082/",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

    def send_message(self, data):
        self.ws.send(data)

    def start(self):
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
