import socket
from .serverconfig import ServerConfig
from threading import Thread

class TCPZoneTransferReceiver(Thread):
    def __init__(self, port):
        super().__init__()
        self.port = port

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiver:
            receiver.bind(('', self.port))
            receiver.listen()
            print(f"Estou à escuta no {receiver.getsockname()}")
            while True:
                conn, addr = receiver.accept()
                with conn:
                    print(f"Connected by {addr}")

class UDPSSTransferSender(Thread):
    def __init__(self, domain, server, server_config):
        super().__init__()
        self.domain = domain
        self.server = server
        self.server_config = server_config

    def run(self):
        refresh_time = self.server_config.get_database_config(self.domain).get_refresh_time(self.domain) 

        while True:
            pass

class UDPClientListener(Thread):
    def __init__(self, queue, port):
        super().__init__()
        self.queue = queue 
        self.port = port
    
    def run(self) -> None:

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:

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
        for server in self.server_config.get_sp_servers():
            UDPSSTransferSender(server[0], server[1], self.server_config)
        UDPClientListener(self.queue, self.port).start()
        TCPZoneTransferReceiver(self.port).start()

    def __str__(self):
        return f"Server(debug_mode = {self.debug_mode}, server_config = {self.server_config}, port = {self.port}, timeout = {self.timeout})"
