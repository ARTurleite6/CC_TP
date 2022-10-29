class DatabaseConfig:
    def __init__(self, database_file):
        self.default = {} 
        self.name = {}
        self.administrator = {}
        self.serial_number = {}
        self.refresh = {}
        self.retry = {}
        self.expire = {}
        self.ns = {}
        self.ips = {}
        self.emails = {}
        self.cname = {}

        self.__read_config_file__(database_file)

    def __str__(self):
        return f"""Database(default = {self.default}
        name = {self.name},
        administrator = {self.administrator},
        serial_number = {self.serial_number}
        refresh = {self.refresh}
        retry = {self.retry}
        expire = {self.expire}
        ns = {self.ns}
        ips = {self.ips}
        emails = {self.emails}
        cname = {self.cname}
        )
        """

    def __read_config_file__(self, database_file):
        with open(database_file) as file:

            for line in filter(lambda x: x[0] != '#', file.read().splitlines()):
                concatable_value = ""
                for (variable, value) in self.default.items():
                    line = line.replace(variable, value)

                camps = line.split(' ')
                param = camps[0]
                type = camps[1]
                value = camps[2]
                ttl = 0
                priority = 255

                tam = len(camps)

                if tam > 4:
                    ttl = int(camps[4])

                if tam > 5:
                    priority = int(camps[5])

                if type == "DEFAULT":
                    if param not in self.default:
                        self.default[param] = value
                    if param == "@":
                        concatable_value = value
                elif type == "SOASP":
                    self.name[param] = (value, ttl)
                elif type == "SOAADMIN":
                    self.administrator[param] = (value, ttl)
                elif type == "SOASERIAL":
                    self.serial_number[param] = (int(value), ttl)
                elif type == "SOAREFRESH":
                    self.refresh[param] = (int(value), ttl)
                elif type == "SOARETRY":
                    self.retry[param] = (int(value), ttl)
                elif type == "SOAEXPIRE":
                    self.expire[param] = (int(value), ttl)
                elif type == "NS":
                    if param not in self.ns:
                        self.ns[param] = {}
                    self.ns[param][value] = (ttl, priority)
                elif type == "A":
                    self.ips[param] = (value, ttl, priority)
                elif type == "CNAME":
                    if value not in self.cname and param not in self.cname:
                        self.cname[param] = (value, ttl)
                elif type == "MX":
                    self.emails[param] = (value, ttl, priority)
                elif type == "PTR":
                    pass 






