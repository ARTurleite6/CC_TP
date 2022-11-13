import socket
from time import sleep
from server_module.tcp import TCPZoneTransferReceiver

from server_module.serverconfig import ServerConfig
from threading import Thread
from utils import from_message_str, DNSMessage
from random import randint

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


class UDPSSTransferSender(Thread):

    def __init__(self, domain: str, server: str, server_config: ServerConfig):
        super().__init__()
        self.domain = domain
        self.server_config = server_config
        camps = server.split(':')
        self.server_ip = camps[0]
        self.port = 5353
        if len(camps) == 2:
            self.port = int(camps[1])
        self.__update_values__()

    def __str__(self):
        return f"UDPSSTransferSender(domain = {self.domain}, server = {self.server_ip}:{self.port}, server_config = {str(self.server_config)}, serial_number = {self.serial_number}, refresh_time = {self.refresh_time})"

    def __update_values__(self) -> None:
        self.serial_number = int(self.server_config.get_database_values(self.domain, "SOASERIAL")[0][0].split(sep=' ', maxsplit=3)[2])
        self.refresh_time = int(self.server_config.get_database_values(self.domain, "SOAREFRESH")[0][0].split(sep=' ', maxsplit=3)[2])
        self.retry_time = int(self.server_config.get_database_values(self.domain, "SOARETRY")[0][0].split(sep=' ', maxsplit=3)[2])
        self.expire_time = int(self.server_config.get_database_values(self.domain, "SOAEXPIRE")[0][0].split(sep=' ', maxsplit=3)[2])
        print(self)

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            message = DNSMessage(randint(1, 65535), (self.domain, "SOASERIAL"), "Q")
            sock.settimeout(10)
            while True:
                print("ola")
                sock.sendto(message.to_message_str(True).encode('utf-8'), (self.server_ip, self.port))
                try:
                    message, addr = sock.recvfrom(1024)
                    print(f"received msg from {addr}")
                    message = from_message_str(message.decode('utf-8'))
                    if message.number_values == 0:
                        print("Provavelmente houve um erro na rececao da mensagem")
                        break;
                    serial_number = int(message.response_values[0].split(' ')[2])
                    if serial_number != self.serial_number:
                        print("vamos tentar")
                        transfer = TCPZoneTransferReceiver(self.server_ip, self.port, self.domain, self.server_config)
                        transfer.start()
                        transfer.join()
                        self.__update_values__()
                    else:
                        print(self)

                    sleep(self.refresh_time)
                except TimeoutError:
                    print("Passou o tempo de timeout")

                    
                

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
        answer = self.server_config.get_database_values(query_value=query_info[0], query_type=query_info[1])
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

