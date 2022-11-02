import socket
from sys import argv
from utils import DNSMessage

def main():
    # if(len(argv) < 5):
    #     return 

    message =  DNSMessage(1, ("example.com.", "MX"), "Q+R") 
    print(message.to_message_str(True))
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #
    # msg = "Adoro redes"
    # s.sendto(msg.encode('utf-8'), ('0.0.0.0', 8080))

if __name__ == "__main__":
    main()
