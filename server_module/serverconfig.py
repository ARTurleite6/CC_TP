from server_module.database import DatabaseConfig
from server_module.database import Origin

class ServerConfig:
    def __init__(self, config_file):
        self.databases_files: dict[str, str] = {}
        self.database_config: DatabaseConfig = DatabaseConfig()
        self.sp_servers: dict[str, str] = {}
        self.ss_servers: dict[str, list[str]] = {}
        self.default_servers: dict[str, list[str]] = {}
        self.log_file = ""
        self.root_servers: list[str] = []
        self.config_from_file(config_file)

    def get_database_config(self) -> DatabaseConfig:
        return self.database_config

    # def add_database_config(self, domain: str, config: DatabaseConfig):
    #     self.database_configs[domain] = config

    def get_sp_servers(self):
        return self.sp_servers.items()

    def __str__(self):
        return f"ServerConfig( databases_configs= {self.database_config}, database_files = {self.databases_files}, sp_servers = {self.sp_servers}, ss_servers= {self.ss_servers}, default_servers= {self.default_servers}, log_file = {self.log_file}, root_servers = {self.root_servers}"

    def config_from_file(self, file: str):

        with open(file) as f:
            file_content = f.read()
            for line in filter(lambda line: line[0] != '#', file_content.splitlines()):
                camps = line.split(" ")
                dom: str = camps[0] + "."
                type: str = camps[1]
                value: str = camps[2]
    
                if type == "DB":
                    self.databases_files[dom] = value
                    with open(value) as file_db:
                        lines = file_db.read()
                        self.database_config.read_config_file(lines, Origin.FILE)
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
                    self.log_file = value
                elif type == "DD":
                    if dom not in self.default_servers:
                        self.default_servers[dom] = []
                    self.default_servers[dom].append(value)


