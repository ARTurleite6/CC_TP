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
    message = s.recv(1024)
    if message:
        message = message.decode('utf-8')
        line_counter = 0
        number_lines = int(message)
        print(message)
        s.sendall(message.encode('utf-8'))

        lines_db = []
        while line_counter < number_lines:
            lines = s.recv(1024)
            if lines:
                lines = lines.decode('utf-8').splitlines()
                for line in lines:
                    line_number = int(line.split(sep=' ', maxsplit=1)[0])
                    if line_counter == line_number:
                        lines_db.append(lines)
                        line_counter += 1
        print(lines_db)

    s.close()

if __name__ == "__main__":
    main()
