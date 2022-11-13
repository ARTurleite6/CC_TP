import socket

from server_module.serverconfig import ServerConfig
from server_module.database import Origin
from threading import Thread

class TCPZoneTransferSender(Thread):
    def __init__(self, server_socket, db_file: str):
        super().__init__()
        self.server_socket = server_socket
        self.db_file = db_file

    def run(self):
        print(f"Abri a transferencia de zona com um cliente")
        # msg = "Vamos la comecar chavalo"
        # self.server_socket.sendall(msg.encode('utf-8'))
        with open(self.db_file) as file:
            content = list(filter(lambda x: x[0] != '#', file.read().splitlines()))
            total_lines = len(content)
            print("tam = ", total_lines)
            self.server_socket.sendall(str(total_lines).encode('utf-8'))
            message = self.server_socket.recv(1024)
            if message:
                number_lines_received = int(message.decode('utf-8'))
                if number_lines_received == total_lines:
                    counter = 0
                    for line in content:
                        message_content = f"{counter} {line}\n"
                        self.server_socket.sendall((message_content.encode('utf-8')))
                        counter += 1
                    
        self.server_socket.close()

class TCPZoneTransferSenderController(Thread):
    def __init__(self, port: int, ss_servers: dict[str, list[str]], files_db: dict[str, str]):
        super().__init__()
        self.port = port
        self.ss_servers = ss_servers
        self.files_db = files_db

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.port))
            print(f"listening on {s.getsockname()[1]}")
            s.listen()
            while True:
                print("outro ciclo")
                connection, address = s.accept()
                domain = connection.recv(1024).decode('utf-8')
                print(f"received message from {address}, message = {domain}")
                if domain in self.ss_servers:
                    servers = self.ss_servers[domain]
                    # for server in servers:
                    #     camps = server.split(':')
                    #     port = 5353
                    #     ip = camps[0]
                    #     if len(camps) == 2:
                    #         port = int(camps[1])
                    #
                    #     # if ip == address[0] and port == address[1]:
                    print("Pode receber")
                    TCPZoneTransferSender(connection, self.files_db[domain]).start()

class TCPZoneTransferReceiver(Thread):
    def __init__(self, server_ip: str, port: int, domain: str, server_config: ServerConfig):
        super().__init__()
        self.domain = domain
        self.port = port
        self.server_ip = server_ip
        self.server_config = server_config

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiver:
            receiver.connect((self.server_ip, self.port))
            msg = self.domain
            receiver.sendall(msg.encode('utf-8'))
            message = receiver.recv(10)
            if message:
                message_dec = message.decode('utf-8')
                number_lines = int(message_dec)
                receiver.sendall(message)

                line_counter = 0
                lines_db = []
                while line_counter < number_lines:
                    lines = receiver.recv(1024)
                    if lines:
                        lines = lines.decode('utf-8').splitlines()
                        for line in lines:
                            line_camps = line.split(sep= ' ', maxsplit=1)
                            line_number = int(line_camps[0])
                            if line_counter == line_number:
                                lines_db.append(line_camps[1])
                                line_counter += 1

                self.server_config.add_database_entries_file(lines_db, Origin.SP, self.domain) 
            

