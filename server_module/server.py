import socket
from server_module.serverconfig import ServerConfig
from threading import Thread
from utils import from_message_str, DNSMessage
from time import sleep

class TCPZoneTransferSender(Thread):
    def __init__(self, server_socket, db_file: str):
        super().__init__()
        self.server_socket = server_socket
        self.db_file = db_file

    def run(self):
        print(f"Abri a transferencia de zona com um cliente")
        msg = "Vamos la comecar chavalo"
        self.server_socket.sendall(msg.encode('utf-8'))
        with open(self.db_file) as file:
            content = list(filter(lambda x: x[0] == '#', file.read().splitlines()))
            print("tam = ", len(content))
            self.server_socket.sendall(str(len(content)).encode('utf-8'))
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
                msg = connection.recv(1024).decode('utf-8')
                print(f"received message from {address}, message = {msg}")
                if msg in self.ss_servers:
                    servers = self.ss_servers[msg]
                    # for server in servers:
                    #     camps = server.split(':')
                    #     port = 5353
                    #     ip = camps[0]
                    #     if len(camps) == 2:
                    #         port = int(camps[1])
                    #
                    #     # if ip == address[0] and port == address[1]:
                    print("Pode receber")
                    TCPZoneTransferSender(connection, self.files_db[msg]).start()

class TCPZoneTransferReceiver(Thread):
    def __init__(self, server: str, domain: str):
        super().__init__()
        camps = server.split(':')
        self.domain = domain
        if len(camps) < 2:
            self.port = 8080
            
        self.port = int(camps[1])
        self.server = camps[0]

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiver:
            receiver.connect((self.server, self.port))
            msg = self.domain
            receiver.sendall(msg.encode('utf-8'))

class UDPSSTransferSender(Thread):

    def __init__(self, domain: str, server: str, refresh_time: int = 0):
        super().__init__()
        self.domain = domain
        # self.refresh_time = domain
        # self.server = server

    def run(self):
        while True:
            pass

class UDPQueryAnswer(Thread):
    def __init__(self, server_config: ServerConfig, client_addr, message: bytes):
        super().__init__()
        self.server_config = server_config
        self.client_addr = client_addr
        self.message = from_message_str(message.decode('utf-8'))

    def run(self) -> None:
        print(self.message)
        print(f"Received from {self.client_addr}")
        query_info = self.message.get_query_info()
        cache = self.server_config.get_database_config()
        answer = cache.get_database_values(query_value=query_info[0], query_type=query_info[1])
        # response = db_config.get_lines_type_domain(query_info[1], query_info[0])
        # authorities = db_config.get_lines_type_domain('NS', query_info[0])
        # ips = []
        #
        # for res in response:
        #     value = res.split(' ')[2]
        #     ips_wanted = db_config.get_lines_type_domain('A', value)
        #     for ip in ips_wanted:
        #         ips.append(ip)
        #
        # for auth in authorities:
        #     value = auth.split(' ')[2]
        #     ips_wanted = db_config.get_lines_type_domain('A', value)
        #     for ip in ips_wanted:
        #         ips.append(ip)
        # print(response)
        # print(authorities)
        # print(ips)
        message = DNSMessage(id=self.message.get_id(), query_info=self.message.get_query_info(), flags="A+R", values=answer[0] + answer[1] + answer[2], number_extra_values=len(answer[2]), number_authorities=len(answer[1]), number_values=len(answer[0]), response_code=0)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.to_message_str(debug_mode=True).encode('utf-8'), self.client_addr)



class UDPClientListener(Thread):
    def __init__(self, port, server_config):
        super().__init__()
        self.port = port
        self.server_config = server_config
    
    def run(self) -> None:

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:

            receiver.bind(('', 0))

            print(f"Estou á escuta no {receiver.getsockname()}")

            while True:
                msg, addr = receiver.recvfrom(1024)
                print(f"received message from {addr}")
                UDPQueryAnswer(self.server_config, addr, msg).start()

    
class Server:
    def __init__(self, port, config_file, timeout, debug_mode = True):
        self.debug_mode = debug_mode
        self.server_config = ServerConfig(config_file=config_file)
        self.port = port
        self.timeout = timeout

    def run(self):
        print(self.server_config.databases_files)
        sss = self.server_config.get_ss_servers()
        dbs_files = self.server_config.get_database_files()

        TCPZoneTransferSenderController(self.port, sss, dbs_files).start()

        # for (domain, servers) in sss.items():
        #     for server in servers:
        #         TCPZoneTransferSender(self.port, server, domain).start() 
        
        sps = self.server_config.get_sp_servers()
        threads: list[TCPZoneTransferReceiver] = []
        for (domain, server) in sps:
            threads.append(TCPZoneTransferReceiver(server, domain))

        for thread in threads:
            thread.start() 

        for thread in threads:
            thread.join()
            
        UDPClientListener(self.port, self.server_config).start()

    def __str__(self):
        return f"Server(debug_mode = {self.debug_mode}, server_config = {self.server_config}, port = {self.port}, timeout = {self.timeout})"
