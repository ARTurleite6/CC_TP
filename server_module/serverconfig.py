import datetime
import logging

from threading import RLock
from server_module.database import DatabaseConfig
from server_module.database import Origin

class ServerConfig:
    def __init__(self, config_file, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.databases_files: dict[str, str] = {}
        self.database_lock = RLock()
        self.log_lock = RLock()
        self.database_config: DatabaseConfig = DatabaseConfig()
        self.sp_servers: dict[str, str] = {}
        self.ss_servers: dict[str, list[str]] = {}
        self.default_servers: dict[str, list[str]] = {}
        self.all_log_file = ""
        self.log_files_domain: set[str] = set()
        self.root_servers: list[str] = []
        self.config_from_file(config_file)

    def has_authority(self, domain: str) -> bool:
        return domain in self.sp_servers or domain in self.ss_servers

    def has_type_for_domain(self, domain: str, type: str) -> bool:
        with self.database_lock:
            return self.database_config.has_type_for_domain(domain, type)

    def has_domain(self, domain: str) -> bool: 
        with self.database_lock:
            return self.database_config.has_domain(domain)

    def get_database_config(self) -> DatabaseConfig:
        with self.database_lock:
            return self.database_config

    def get_database_values(self, query_value: str, query_type: str):
        with self.database_lock:
            return self.database_config.get_database_values(query_value, query_type)

    def get_database_files(self) -> dict[str, str]:
        return self.databases_files

    def add_database_entries_file(self, database_file: list[str], origin: Origin, dom: str):
        with self.database_lock:
            self.database_config.read_config_file(database_file, origin, dom)

    def get_ss_servers(self) -> dict[str, list[str]]:
        return self.ss_servers

    def get_sp_servers(self) -> dict[str, str]:
        return self.sp_servers

    def __str__(self):
        with self.database_lock:
            return f"ServerConfig( databases_configs= {self.database_config}, database_files = {self.databases_files}, sp_servers = {self.sp_servers}, ss_servers= {self.ss_servers}, default_servers= {self.default_servers}, log_file = {self.all_log_file}, root_servers = {self.root_servers}, log_files_domain = {self.log_files_domain}"

    def log_info(self, domain: str, message: str):
        with self.log_lock:
            logger = logging.getLogger(domain) 
            logger.warning(message)

    def config_from_file(self, file: str):

        with open(file) as f:

            time_initialized_read = datetime.datetime.now()

            file_content = f.read()
            for line in filter(lambda line: line[0] != '#', file_content.splitlines()):
                camps = line.split(" ")
                dom: str = camps[0]
                if dom != 'all':
                    dom += "."
                type: str = camps[1]
                value: str = camps[2]
    
                if type == "DB":
                    self.databases_files[dom] = value
                    with open(value) as file_db:
                        lines = file_db.read().splitlines()
                        with self.database_lock:
                            time_read = datetime.datetime.now()
                            self.log_info("all", f"{time_read} EV @ db-file-read {value}")
                            self.database_config.read_config_file(lines, Origin.FILE, dom)
                elif type == "SP":
                    self.sp_servers[dom] = value
                elif type == "SS":
                    if dom not in self.ss_servers:
                        self.ss_servers[dom] = []
                    self.ss_servers[dom].append(value)
                elif type == "ST":
                    with open(value) as root_file:
                        for server in filter(lambda line: line[0] != '#', root_file.read().splitlines()):
                            self.root_servers.append(server)
                elif type == "LG":
                    if dom == "all":
                        self.all_log_file = value
                    else:
                        self.log_files_domain.add(dom)

                    format = logging.Formatter("%(message)s")
                    file_handler = logging.FileHandler(value)
                    file_handler.setLevel(logging.DEBUG)
                    file_handler.setFormatter(format)

                    logger = logging.getLogger(dom)
                    logger.addHandler(file_handler)
                    if self.debug_mode:
                        console_handler = logging.StreamHandler()
                        console_handler.setLevel(logging.DEBUG)
                        console_handler.setFormatter(format)
                        logger.addHandler(console_handler)

                elif type == "DD":
                    if dom not in self.default_servers:
                        self.default_servers[dom] = []
                    self.default_servers[dom].append(value)

            self.log_info("all", f"{time_initialized_read} EV @ conf-file-read {file}")


