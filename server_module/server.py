import signal
import sys

from server_module.udp import UDPClientListener, UDPSSTransferSender
from server_module.serverconfig import ServerConfig
from server_module.tcp import TCPZoneTransferSenderController, transfer_zone_receive
from threading import Thread
from datetime import datetime
    
class Server:
    def __init__(self, port, config_file, timeout, debug_mode = True):
        self.debug_mode = debug_mode
        self.server_config = ServerConfig(config_file=config_file, debug_mode=debug_mode)
        self.port = port
        self.timeout = timeout

    def run(self):

        signal.signal(signal.SIGINT, self.shutdown)

        mode = "debug" if self.debug_mode else "shy"
        self.server_config.log_info("all", f"{datetime.now()} ST 127.0.0.1 {self.timeout} {mode}")
        TCPZoneTransferSenderController(self.port,  self.server_config).start()

        sps = self.server_config.get_sp_servers()
        threads: list[Thread] = []
        for (domain, server) in sps.items():
            camps = server.split(':')
            server_ip = camps[0]
            port = 5353 
            if len(camps) == 2:
                port = int(camps[1])
            threads.append(Thread(target=transfer_zone_receive, args=(server_ip, port, domain, self.server_config)))

        for thread in threads:
            thread.start() 

        for thread in threads:
            thread.join()
        UDPClientListener(self.port, self.server_config, self.timeout).start()

        for (domain, server) in sps.items():
            UDPSSTransferSender(domain=domain, server=server, server_config=self.server_config, ttl=self.timeout).start()

    def shutdown(self, _signal_number_, _frame):
        self.server_config.log_info("all", f"{datetime.now} SP 127.0.0.1 Terminated SIGINT")
        sys.exit()

    def __str__(self):
        return f"Server(debug_mode = {self.debug_mode}, server_config = {self.server_config}, port = {self.port}, timeout = {self.timeout})"
