import socket
from sys import argv
from utils import DNSMessage

def main():
    # if(len(argv) < 5):
    #     return 

    message =  DNSMessage(1, ("example.com.", "MX"), "Q+R") 
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(message.to_message_str(True).encode('utf8'), ('0.0.0.0', 8080))
        message, _ = s.recvfrom(1024)
        print(message.decode('utf-8'))

if __name__ == "__main__":
    main()
