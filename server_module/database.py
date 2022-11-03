class DatabaseConfig:
    def __init__(self, database_file):
        self.default: dict[str, str] = {} 
        self.name: dict[str, tuple[str, int]] = {}
        self.administrator: dict[str, tuple[str, int]] = {}
        self.serial_number: dict[str, tuple[int, int]] = {}
        self.refresh: dict[str, tuple[int, int]] = {}
        self.retry: dict[str, tuple[int, int]] = {}
        self.expire: dict[str, tuple[int, int]] = {}
        self.ns: dict[str, list[tuple[str, int, int]]] = {}
        self.ips: dict[str, tuple[str, int, int]] = {}
        self.emails: dict[str, list[tuple[str, int, int]]] = {}
        self.cname: dict[str, tuple[str, int]] = {}

        self.lines: dict[str, list[str]] = {}

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

    def get_lines_type_domain(self, type, wanted_domain):
        values = []
        lines_type = self.lines[type]
        for line in lines_type:
            domain = line.split(' ')[0]
            if domain == wanted_domain:
                values.append(line)
        return values

    def get_emails(self, domain) -> list[tuple[str, int, int]]:
        return self.emails[domain]

    def get_authorities(self, domain) -> list[tuple[str, int, int]]:
        return self.ns[domain]

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

                if type not in self.lines:
                    self.lines[type] = []
                self.lines[type].append(line)

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
                        self.ns[param] = []
                    self.ns[param].append((value, ttl, priority))
                elif type == "A":
                    self.ips[param] = (value, ttl, priority)
                elif type == "CNAME":
                    if value not in self.cname and param not in self.cname:
                        self.cname[param] = (value, ttl)
                elif type == "MX":
                    if param not in self.emails:
                        self.emails[param] = []
                    self.emails[param].append((value, ttl, priority))
                elif type == "PTR":
                    pass 






