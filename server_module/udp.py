import socket
from time import sleep
from datetime import datetime
from server_module.tcp import transfer_zone_receive

from server_module.serverconfig import ServerConfig
from threading import Thread
from utils import from_message_str, DNSMessage
from random import randint

class UDPClientListener(Thread):
    def __init__(self, port: int, server_config: ServerConfig, ttl: int):
        super().__init__()
        self.port = port
        self.server_config = server_config
        self.ttl = ttl
    
    def run(self) -> None:

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:

            receiver.bind(('', self.port))

            print(f"Estou á escuta no {receiver.getsockname()}")

            while True:
                msg, addr = receiver.recvfrom(1024)
                print(f"received message from {addr}")
                UDPQueryAnswer(self.server_config, addr, msg, self.ttl).start()


class UDPSSTransferSender(Thread):

    def __init__(self, domain: str, server: str, server_config: ServerConfig, ttl: int):
        super().__init__()
        self.domain = domain
        self.server_config = server_config
        self.ttl = ttl
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
            sock.settimeout(self.ttl)
            while True:
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
                        transfer_status = transfer_zone_receive(domain=self.domain, server_ip=self.server_ip, port=self.port, server_config=self.server_config)
                        if transfer_status:
                            self.__update_values__()
                            sleep(self.refresh_time)
                        else:
                            self.server_config.log_info(domain=self.domain, message=f"{datetime.now()} EZ {self.server_ip} SS") 
                            sleep(self.retry_time)
                    else:
                        sleep(self.refresh_time)
                except TimeoutError:
                    print("Passou o tempo de timeout")
                    sleep(self.retry_time)


class UDPQueryAnswer(Thread):
    def __init__(self, server_config: ServerConfig, client_addr, message: bytes, ttl: int):
        super().__init__()
        self.server_config = server_config
        self.client_addr = client_addr
        self.message = from_message_str(message.decode('utf-8'))
        self.ttl = ttl

    def run(self) -> None:
        print(self.message)
        print(f"Received from {self.client_addr}")
        self.server_config.log_info("all", f"{datetime.now()} QR {self.client_addr[0]} {self.message.to_message_str()}")
        query_info = self.message.get_query_info()
        answer = self.server_config.get_database_values(query_value=query_info[0], query_type=query_info[1])

        flags = "R+A"

        message = DNSMessage(id=self.message.get_id(), query_info=self.message.get_query_info(), flags=flags, values=answer[0] + answer[1] + answer[2], number_extra_values=len(answer[2]), number_authorities=len(answer[1]), number_values=len(answer[0]), response_code=0)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.to_message_str(debug_mode=True).encode('utf-8'), self.client_addr)
            self.server_config.log_info("all", f"{datetime.now()} RP {self.client_addr[0]} {message.to_message_str()}")

