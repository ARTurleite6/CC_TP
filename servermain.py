from sys import argv
from server_module import Server

def main():
    if len(argv) < 4:
        print("poucos argumentos, pass [porta, timeout, ficheiro de configuração, (debug)]")
        return 

    debug = False
    if len(argv) == 5 and argv[4] == 'D':
        debug = True
     
    server = Server(port=int(argv[1]), timeout=int(argv[2]), debug_mode=debug, config_file=argv[3])

    server.run()

if __name__ == "__main__":
    main()
