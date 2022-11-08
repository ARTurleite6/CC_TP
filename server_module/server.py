import socket
from server_module.serverconfig import ServerConfig
from threading import Thread
from utils import from_message_str, DNSMessage
# class TCPZoneTransferReceiver(Thread):
#     def __init__(self, port):
#         super().__init__()
#         self.port = port
#
#     def run(self):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiver:
#             receiver.bind(('', self.port))
#             receiver.listen()
#             print(f"Estou à escuta no {receiver.getsockname()}")
#             while True:
#                 conn, addr = receiver.accept()
#                 with conn:
#                     print(f"Connected by {addr}")

# class UDPSSTransferSender(Thread):
#     def __init__(self, domain, server, server_config):
#         super().__init__()
#         self.domain = domain
#         self.server = server
#         self.server_config = server_config
#
#     def run(self):
#         refresh_time = self.server_config.get_database_config(self.domain).get_refresh_time(self.domain) 
#
#         while True:
#             pass

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

            receiver.bind(('', self.port))

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
        print(self.server_config.database_config)
        UDPClientListener(self.port, self.server_config).start()

    def __str__(self):
        return f"Server(debug_mode = {self.debug_mode}, server_config = {self.server_config}, port = {self.port}, timeout = {self.timeout})"
