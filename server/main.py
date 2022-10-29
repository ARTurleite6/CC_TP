
from server import Server
from sys import argv

def main():
    if len(argv) < 4:
        print("poucos argumentos, pass [porta, timeout, ficheiro de configuração, (debug)]")
        return 

    debug = True
    if len(argv) == 5:
        debug = bool(argv[4])
     
    server = Server(port=int(argv[1]), timeout=int(argv[2]), debug_mode=debug, config_file=argv[3])

    server.run()

if __name__ == "__main__":
    main()
