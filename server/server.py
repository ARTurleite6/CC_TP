import socket
from serverconfig import ServerConfig
from time import sleep
from threading import Thread

class UDPClientListener(Thread):
    def __init__(self, queue, port):
        super().__init__()
        self.queue = queue 
        self.port = port
    
    def run(self) -> None:

        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        receiver.bind(('', self.port))

        print(f"Estou á escuto no {receiver.getsockname()}")

        while True:
            msg, _ = receiver.recvfrom(1024)
            print(msg.decode('utf-8'))
    
class Server:
    def __init__(self, port, config_file, timeout, debug_mode = True):
        self.debug_mode = debug_mode
        self.server_config = ServerConfig(config_file=config_file)
        self.port = port
        self.timeout = timeout
        self.queue = []

    def run(self):
        UDPClientListener(self.queue, self.port).start()

    def __str__(self):
        return f"Server(debug_mode = {self.debug_mode}, server_config = {self.server_config}, port = {self.port}, timeout = {self.timeout})"
