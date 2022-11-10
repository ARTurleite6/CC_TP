import socket
from sys import argv
from time import sleep
from utils import DNSMessage

def main():
    # if(len(argv) < 5):
    #     return 

    message =  DNSMessage(1, ("example.com.", "MX"), "Q+R") 
    print(message.to_message_str())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msg = "example.com"
    # s.sendto(message.to_message_str(True).encode('utf-8'), ('0.0.0.0', 8080))
    s.connect(('0.0.0.0', 8080))
    s.sendall(msg.encode('utf-8'))
    while True:
        message, _ = s.recvfrom(1024)
        if message:
            print(message.decode('utf-8'))
    s.close()

if __name__ == "__main__":
    main()
