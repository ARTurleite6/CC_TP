import socket

from datetime import datetime, timedelta
from server_module.serverconfig import ServerConfig
from server_module.database import Origin
from threading import Thread

TTL_TRANSFER = 5

class TCPZoneTransferSender(Thread):
    def __init__(self, server_socket, db_file: str, server_config: ServerConfig, domain: str):
        super().__init__()
        self.server_socket = server_socket
        self.db_file = db_file
        self.server_config = server_config
        self.domain = domain

    def run(self):
        # msg = "Vamos la comecar chavalo"
        # self.server_socket.sendall(msg.encode('utf-8'))
        with open(self.db_file) as file:
            content = list(filter(lambda x: x[0] != '#', file.read().splitlines()))
            total_lines = len(content)
            self.server_socket.sendall(str(total_lines).encode('utf-8'))
            message = self.server_socket.recv(1024)
            if message:
                number_lines_received = int(message.decode('utf-8'))
                if number_lines_received == total_lines:
                    counter = 0
                    for line in content:
                        message_content = f"{counter} {line}\n"
                        try:
                            self.server_socket.sendall((message_content.encode('utf-8')))
                        except OSError:
                            print("client closed")
                            break
                        counter += 1
                    if counter == total_lines:
                        self.server_config.log_info(self.domain, f"{datetime.now()} ZT {self.server_socket.getsockname()} SP")
                    else:
                        self.server_config.log_info(self.domain, f"{datetime.now()} EZ {self.server_socket.getsockname()} SP")

        self.server_socket.close()

class TCPZoneTransferSenderController(Thread):
    def __init__(self, port: int, server_config: ServerConfig):
        super().__init__()
        self.port = port
        self.server_config = server_config

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            ss_servers = self.server_config.get_ss_servers()
            files_db = self.server_config.get_database_files()
            s.bind(('', self.port))
            print(f"listening on {s.getsockname()}")
            s.listen()
            while True:
                connection, address = s.accept()
                domain = connection.recv(1024).decode('utf-8')
                print(f"received message from {address}, message = {domain}")
                if domain in ss_servers:
                    servers = ss_servers[domain]
                    for server in servers:
                        camps = server.split(':')
                        port = 5353
                        ip = camps[0]
                        if len(camps) == 2:
                            port = int(camps[1])

                        if ip == address[0] and port == address[1]:
                            TCPZoneTransferSender(connection, files_db[domain], self.server_config, domain).start()

def transfer_zone_receive(server_ip: str, port: int, domain: str, server_config: ServerConfig) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiver:
        receiver.connect((server_ip, port))
        msg = domain
        receiver.sendall(msg.encode('utf-8'))
        message = receiver.recv(10)
        # test if received message
        if message:
            message_dec = message.decode('utf-8')
            number_lines = int(message_dec)
            receiver.sendall(message)
            line_counter = 0
            lines_db = []
            wait_time = datetime.now() + timedelta(seconds=TTL_TRANSFER)
            break_loop = False
            while not break_loop and line_counter < number_lines:
                lines = receiver.recv(1024)
                if lines:
                    lines = lines.decode('utf-8').splitlines()
                    for line in lines:
                        line_camps = line.split(sep= ' ', maxsplit=1)
                        line_number = int(line_camps[0])
                        if line_counter == line_number:
                            lines_db.append(line_camps[1])
                            line_counter += 1
                if wait_time < datetime.now():
                    break_loop = True

            if line_counter == number_lines:
                server_config.add_database_entries_file(lines_db, Origin.SP, domain) 
                return True
        return False
