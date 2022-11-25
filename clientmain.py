import socket
from sys import argv
from utils import DNSMessage
from random import randint

from utils.dns import from_message_str

TTL = 3

def main():
    if(len(argv) < 4):
        return 

    server = argv[1]
    server_port = 5353
    camps = server.split(':')
    server_ip = camps[0]
    if len(camps) == 2:
        server_port = int(camps[1])
    query_value = argv[2]
    # if query_value[-1] != '.':
    #     query_value += '.'

    query_type = argv[3]
    recursive_mode = False

    if(len(argv) == 5):
        if argv[4] == "R":
            recursive_mode = True

    number_time_sent = 0

    MAX_TIME_SENT = 3

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
        soc.settimeout(TTL)
        flags = "Q"
        if recursive_mode:
            flags += "+R"

        message = DNSMessage(id=randint(1, 65535), query_info=(query_value, query_type), flags=flags)

        message_received = False
        while not message_received and number_time_sent < MAX_TIME_SENT:
            soc.sendto(message.to_message_str().encode('utf-8'), (server_ip, server_port))
            number_time_sent += 1

            try:
                msg = soc.recv(1024)
                if msg:
                    msg = msg.decode('utf-8')
                    print(from_message_str(msg))
                    message_received = True
            
            except TimeoutError:
                print("timeout, gonna ask the query again")

        if not message_received:
            print("Não consegui obter qualquer resposta")

if __name__ == "__main__":
    main()
