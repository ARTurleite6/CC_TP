from database import DatabaseConfig

class ServerConfig:
    def __init__(self, config_file):
        self.databases = {}
        self.sp_servers = {}
        self.ss_servers = {}
        self.default_servers = {}
        self.log_file = ""
        self.root_servers = []
        self.config_from_file(config_file)

    def __str__(self):
        return f"ServerConfig( databases= {self.databases}, sp_servers = {self.sp_servers}, ss_servers= {self.ss_servers}, default_servers= {self.default_servers}, log_file = {self.log_file}, root_servers = {self.root_servers}"

    def config_from_file(self, file: str):

        with open(file) as f:
            file_content = f.read()
            for line in filter(lambda line: line[0] != '#', file_content.splitlines()):
                camps = line.split(" ")
                dom: str = camps[0]
                type: str = camps[1]
                value: str = camps[2]
    
                if type == "DB":
                    db_config = DatabaseConfig(value)
                    print(db_config)
                    self.databases[dom] = db_config
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
                    self.default_servers[dom] = value


