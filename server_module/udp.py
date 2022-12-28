import socket
from time import sleep
from datetime import datetime
from server_module.database import cache_entry_from_str, Origin
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

    def __check_valid_camps__(self) -> bool:
        values = self.server_config.get_database_values(self.domain, "SOASERIAL")[0]
        if len(values) == 0:
            return False

        return True

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
                    if not self.__check_valid_camps__() or serial_number != self.serial_number:
                        transfer_status = transfer_zone_receive(domain=self.domain, server_ip=self.server_ip, port=self.port, server_config=self.server_config)
                        if transfer_status:
                            self.server_config.log_info(domain=self.domain, message=f"{datetime.now()} ZT {self.server_ip} SS") 
                            self.__update_values__()
                            self.server_config.add_expire_ss_timer(self.domain, self.expire_time)
                            sleep(self.refresh_time)
                        else:
                            print("erro transferencia")
                            self.server_config.log_info(domain=self.domain, message=f"{datetime.now()} EZ {self.server_ip} SS") 
                            sleep(self.retry_time)
                    else:
                        sleep(self.refresh_time)
                except TimeoutError:
                    self.server_config.log_info(self.domain, f"{datetime.now()} TO {self.server_ip} DBVersion")
                    sleep(self.retry_time)


class UDPQueryAnswer(Thread):
    def __init__(self, server_config: ServerConfig, client_addr, message: bytes, ttl: int):
        super().__init__()
        self.server_config = server_config
        self.client_addr = client_addr
        self.message = from_message_str(message.decode('utf-8'))
        self.ttl = ttl

    def run(self) -> None:
        print(f"Received from {self.client_addr}")
        query_info = self.message.get_query_info()
        self.server_config.log_info(query_info[0], f"{datetime.now()} QR {self.client_addr[0]} {self.message.to_message_str()}")
        if self.server_config.can_answer_domain(query_info[0]):
            answer = self.server_config.get_database_values(query_value=query_info[0], query_type=query_info[1])

            if len(answer[0]) == 0:
                answer = self.get_answer(query_info[0])
                if answer is not None:
                    self.send_answer(answer)
            else:
                flags = ""
                if(self.server_config.has_authority(query_info[0])):
                    flags = "A"
                message = DNSMessage(id=self.message.get_id(), query_info=self.message.get_query_info(), flags=flags, values=answer[0] + answer[1] + answer[2], number_extra_values=len(answer[2]), number_authorities=len(answer[1]), number_values=len(answer[0]), response_code=0)
                self.send_answer(message)
                # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                #     s.sendto(message.to_message_str(debug_mode=True).encode('utf-8'), self.client_addr)
                #     self.server_config.log_info(query_info[0], f"{datetime.now()} RP {self.client_addr[0]} {message.to_message_str()}")

    def get_answer(self, domain: str) -> DNSMessage | None:
        if self.server_config.am_i_sr():
            closer_domain = self.server_config.database_config.get_closer_domain_with_auth(domain)
            authorities = []
            if closer_domain is None:
                authorities = self.server_config.get_root_servers()
            else:
                authorities = list(map(lambda entry: entry.split(' ')[2], self.server_config.get_database_values(closer_domain, "NS")[2]))
            auth = 0
                # found = False
            while auth < len(authorities):
                print("authorities to call =", authorities[auth])
                message = send_question(self.ttl, self.message, ip_from_str(authorities[auth]), self.server_config)
                if message is None:
                    print("Nao tive resposta")
                    auth += 1
                else:
                    print(message)

                    for res in message.response_values + message.auth_values + message.extra_values:
                        self.server_config.database_config.add_entry(cache_entry_from_str(res, origem=Origin.OTHER))
                    print(self.server_config.database_config)
                    if message.response_code == 0 or message.response_code == 2:
                        message.flags = [0, 0, 0]
                        return message
                    else:
                        authorities = list(map(lambda value: value.split(' ')[2], message.extra_values))
                        print(authorities)

            return None
                
        else:
            closer_domain = self.server_config.database_config.get_closer_domain_with_auth(domain)
            if closer_domain is None:
                print("deu none")
                closer_domain = "."
            response_code = 1
            if self.server_config.has_authority(closer_domain):
                response_code = 2
            answer = self.server_config.get_database_values(closer_domain, "NS")
            message = DNSMessage(id=self.message.get_id(), query_info=self.message.get_query_info(), flags="A", values=answer[1] + answer[2], number_extra_values=len(answer[2]), number_authorities=len(answer[1]), number_values=0, response_code=response_code)
            self.send_answer(message)


    def send_answer(self, message: DNSMessage):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.to_message_str(debug_mode=True).encode('utf-8'), self.client_addr)
            self.server_config.log_info(message.get_query_info()[0], f"{datetime.now()} RP {self.client_addr[0]} {message.to_message_str()}")


def send_question(ttl: int, message: DNSMessage, ip: tuple[str, int], server_config: ServerConfig | None = None) -> DNSMessage | None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        tries = 0
        s.settimeout(ttl)
        while tries < 3:
            try:
                s.sendto(message.to_message_str(debug_mode=True).encode('utf-8'), ip)
                if server_config is not None:
                    server_config.log_info(message.get_query_info()[0], f"{datetime.now()} QE {ip[0]} {message.to_message_str()}")

                answer = s.recv(1024)
                answer = answer.decode('utf-8')
                answer = from_message_str(answer)
                if server_config is not None:
                    server_config.log_info(message.get_query_info()[0], f"{datetime.now()} RR {ip[0]} {answer.to_message_str()}")
                return answer
            except TimeoutError:
                print("Passou o timeout")
                tries += 1
    return None

def ip_from_str(string: str) -> tuple[str, int]:
    camps = string.split(':')
    port = 5353
    if len(camps) == 2:
        port = int(camps[1])

    return camps[0], port
