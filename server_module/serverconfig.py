import datetime
import logging
import sys

from exceptions import SameDomainSPSSexception
from threading import RLock
from exceptions import NonSPSSServerLogFileException
from exceptions.serverexceptions import AllLogFileNotReceivedException, NonDBWithSSEntryException
from server_module.database import CacheConfig
from server_module.database import Origin

class ServerConfig:
    def __init__(self, config_file, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.databases_files: dict[str, str] = {}
        self.log_lock = RLock()
        self.database_config: CacheConfig = CacheConfig()
        self.sp_servers: dict[str, str] = {}
        self.ss_servers: dict[str, list[str]] = {}
        self.default_servers: dict[str, list[str]] = {}
        self.all_log_file = ""
        self.log_files_domain: set[str] = set()
        self.root_servers: list[str] = []
        try:
            self.config_from_file(config_file)
        except SameDomainSPSSexception:
            self.log_info("all", f"{datetime.datetime.now()} FL 127.0.0.1 Server is SP and SS for the same domain") 
            self.log_info("all", f"{datetime.datetime.now()} SP 127.0.0.1 Error reading config file")
            sys.exit()
        except NonSPSSServerLogFileException:
            self.log_info("all", f"{datetime.datetime.now()} FL 127.0.0.1 Received a log file for a domain which server isn´t SP nor SS")
        except AllLogFileNotReceivedException:
            self.log_info("all", f"{datetime.datetime.now()} FL 127.0.0.1 Server didn´t receive a entry for a all log file")
        except NonDBWithSSEntryException:
            self.log_info("all", f"{datetime.datetime.now()} FL 127.0.0.1 Server didn´t receive a DB file for SS entries")
            self.log_info("all", f"{datetime.datetime.now()} SP 127.0.0.1 Error reading config file")
            sys.exit()

    def can_answer_domain(self, domain: str) -> bool:
        if len(self.default_servers) == 0:
            return True

        return domain in self.default_servers

    def add_expire_ss_timer(self, domain: str, expire_time: int):
        self.database_config.add_expire_ss_timer(domain, expire_time)

    def has_authority(self, domain: str) -> bool:
        return domain in self.sp_servers or domain in self.ss_servers

    def has_type_for_domain(self, domain: str, type: str) -> bool:
        return self.database_config.has_type_for_domain(domain, type)

    def has_domain(self, domain: str) -> bool: 
        return self.database_config.has_domain(domain)

    def get_database_config(self) -> CacheConfig:
        return self.database_config

    def get_database_values(self, query_value: str, query_type: str):
        return self.database_config.get_cache_values(query_value, query_type)

    def get_database_files(self) -> dict[str, str]:
        return self.databases_files

    def add_database_entries_file(self, database_file: list[str], origin: Origin, dom: str):
        self.database_config.read_database_file(database_file, origin, dom)

    def get_ss_servers(self) -> dict[str, list[str]]:
        return self.ss_servers

    def get_sp_servers(self) -> dict[str, str]:
        return self.sp_servers

    def log_info(self, domain: str, message: str):
        with self.log_lock:
            if domain in self.log_files_domain: 
                logger = logging.getLogger(domain) 
                logger.warning(message)
            else:
                logger = logging.getLogger("all")
                logger.warning(message)

    def __set_logger_file__(self, dom, value):
        format = logging.Formatter("%(message)s")
        file_handler = logging.FileHandler(value)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(format)

        logger = logging.getLogger(dom)
        logger.addHandler(file_handler)
        if self.debug_mode:
            print("console mode")
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(format)
            logger.addHandler(console_handler)
            

    def __str__(self):
            return f"ServerConfig( databases_configs= {self.database_config}, database_files = {self.databases_files}, sp_servers = {self.sp_servers}, ss_servers= {self.ss_servers}, default_servers= {self.default_servers}, log_file = {self.all_log_file}, root_servers = {self.root_servers}, log_files_domain = {self.log_files_domain}"

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
                    # with open(value) as file_db:
                    #     lines = file_db.read().splitlines()
                    #     with self.database_lock:
                    #         time_read = datetime.datetime.now()
                    #         self.log_info("all", f"{time_read} EV @ db-file-read {value}")
                    #         self.database_config.read_config_file(lines, Origin.FILE, dom)
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

                    self.__set_logger_file__(dom, value)
                    # format = logging.Formatter("%(message)s")
                    # file_handler = logging.FileHandler(value)
                    # file_handler.setLevel(logging.DEBUG)
                    # file_handler.setFormatter(format)
                    #
                    # logger = logging.getLogger(dom)
                    # logger.addHandler(file_handler)
                    # if self.debug_mode:
                    #     print("console mode")
                    #     console_handler = logging.StreamHandler()
                    #     console_handler.setLevel(logging.DEBUG)
                    #     console_handler.setFormatter(format)
                    #     logger.addHandler(console_handler)

                elif type == "DD":
                    if dom not in self.default_servers:
                        self.default_servers[dom] = []
                    self.default_servers[dom].append(value)

            self.log_info("all", f"{time_initialized_read} EV @ conf-file-read {file}")

        for dom in self.ss_servers.keys():
            if dom not in self.databases_files:
                raise NonDBWithSSEntryException()

        #Reading all database files
        for dom, value in self.databases_files.items():
            if dom in self.sp_servers:
                raise SameDomainSPSSexception()
            with open(value) as file_db:
                lines = file_db.read().splitlines()
                time_read = datetime.datetime.now()
                self.log_info(dom, f"{time_read} EV @ db-file-read {value}")
                self.database_config.read_database_file(lines, Origin.FILE, dom)

        #Test if the server as a all log entry
        if self.all_log_file == "":
            self.all_log_file = "var/dns/all.log"
            self.__set_logger_file__("all", self.all_log_file)
            raise AllLogFileNotReceivedException()

        #Test if all server is SP or SS for log files
        for log_file in self.log_files_domain:
            if log_file not in self.databases_files or self.sp_servers:
                raise NonSPSSServerLogFileException()



