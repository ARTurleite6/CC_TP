from enum import Enum


class Status(Enum):
    FREE = 0
    VALID = 1

class Origin(Enum):
    FILE = 0
    STATUS = 1
    OTHER = 2

class CacheEntry:
    def __init__(self, parametro: str = "", tipo: str = "", valor: str = "", ttl: str = "", prioridade: str = "", origem: Origin = Origin.OTHER, tempo_em_cache: int = 0, status: Status = Status.FREE):
        self.parametro = parametro
        self.tipo = tipo
        self.valor = valor
        self.ttl = ttl
        self.prioridade = prioridade
        self.origem = origem
        self.tempo_em_cache = tempo_em_cache
        self.status = status

    def get_entry_as_line(self):
        return f"{self.parametro} {self.tipo} {self.valor} {self.ttl} {self.prioridade}"

    def __str__(self):
        return f"CacheEntry(parametro={self.parametro}, tipo={self.tipo}, valor={self.valor}, ttl={self.ttl}, prioridade={self.prioridade}, origem={self.origem}, tempo_em_cache={self.tempo_em_cache}, status={self.status})"

class DatabaseConfig:
    def __init__(self, infos: list[CacheEntry] = []):
        self.infos = infos

    def add_entry(self, entry: CacheEntry):
        self.infos.append(entry)

    def __str__(self):
        string = "DatabaseConfig("
        for inf in self.infos:
            string += inf.__str__() + ", \n"

        string +=");"
        return string;
            

    def get_database_values(self, query_value, query_type) -> tuple[list[str], list[str], list[str]]:
        res: list[CacheEntry] = []
        auths: list[CacheEntry]= []
        ips: list[CacheEntry] = []
        for entry in self.infos:
            if (entry.parametro == query_value and entry.tipo == query_type):
                print(entry)
                res.append(entry)
            elif query_value == entry.parametro and entry.tipo == "NS":
                print(entry)
                auths.append(entry)

        for value in res:
            for entry in self.infos:
                if value.valor == entry.parametro:
                    ips.append(entry)

        for value in auths:
            for entry in self.infos:
                if value.valor == entry.parametro:
                    ips.append(entry)

        res_str = list(map(lambda entry: entry.get_entry_as_line(), res))
        auths_str = list(map(lambda entry: entry.get_entry_as_line(), auths))
        ips_str = list(map(lambda entry: entry.get_entry_as_line(), ips))

        return(res_str, auths_str, ips_str)

    # def get_lines_type_domain(self, type, wanted_domain):
    #     values = []
    #     lines_type = self.lines[type]
    #     for line in lines_type:
    #         domain = line.split(' ')[0]
    #         if domain == wanted_domain:
    #             values.append(line)
    #     return values

    # def get_emails(self, domain: str) -> list[tuple[str, int, int]]:
    #     return self.emails[domain]
    #
    # def get_authorities(self, domain: str) -> list[tuple[str, int, int]]:
    #     return self.ns[domain]

    def __concat_default_value__(self, words: list[str], concat_value: str) -> list[str]:
        if concat_value == "":
            return words

        if words[0][-1] != '.':
            words[0] += '.' + concat_value

        if not words[2].isdigit() and not self.__is_an_ip__(words[2]) and words[2][-1] != '.':
            words[2] += '.' + concat_value
            
        return words
            

    def __is_an_ip__(self, value: str) -> bool:
        camps = value.split('.')
        return len(camps) == 4 and all(camp.isdigit() for camp in camps)
        

    def read_config_file(self, database_file: str, origin: Origin):


        default = {}

        concatable_value = ""
        for line in filter(lambda x: x[0] != '#', database_file.splitlines()):
            for (variable, value) in default.items():
                line = line.replace(variable, value)

            camps = line.split(' ')
            type = camps[1]
            ttl = "0"
            priority = "255"

            tam = len(camps)

            if tam > 4:
                ttl = camps[4]

            if tam > 5:
                priority = camps[5]

            if type != "DEFAULT":
                camps = self.__concat_default_value__(camps, concatable_value)

            # if type not in self.lines:
            #     self.lines[type] = []
            # self.lines[type].append(" ".join(camps))

            param = camps[0]
            value = camps[2]
            #
            if type == "DEFAULT":
                if param not in default:
                    default[param] = value
                    if param == "@":
                        concatable_value = value
                # elif type == "SOASP":
                #     self.name[param] = (value, ttl)
                # elif type == "SOAADMIN":
                #     self.administrator[param] = (value, ttl)
                # elif type == "SOASERIAL":
                #     self.serial_number[param] = (int(value), ttl)
                # elif type == "SOAREFRESH":
                #     self.refresh[param] = (int(value), ttl)
                # elif type == "SOARETRY":
                #     self.retry[param] = (int(value), ttl)
                # elif type == "SOAEXPIRE":
                #     self.expire[param] = (int(value), ttl)
                # elif type == "NS":
                #     if param not in self.ns:
                #         self.ns[param] = []
                #     self.ns[param].append((value, ttl, priority))
                # elif type == "A":
                #     self.ips[param] = (value, ttl, priority)
                # elif type == "CNAME":
                #     if value not in self.cname and param not in self.cname:
                #         self.cname[param] = (value, ttl)
                # elif type == "MX":
                #     if param not in self.emails:
                #         self.emails[param] = []
                #     self.emails[param].append((value, ttl, priority))
                # elif type == "PTR":
                #     pass 
                # 
            self.infos.append(CacheEntry(parametro=param, tipo=type, valor=value, ttl=ttl, prioridade=priority, origem=origin, tempo_em_cache=0, status=Status.VALID))






