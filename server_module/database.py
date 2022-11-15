from enum import Enum


class Status(Enum):
    FREE = 0
    VALID = 1

class Origin(Enum):
    FILE = 0
    SP = 1
    OTHER = 2

class CacheEntry:
    def __init__(self, parametro: str = "", tipo: str = "", valor: str = "", ttl: str = "", prioridade: str = "", origem: Origin = Origin.OTHER, tempo_em_cache: int = 0, status: Status = Status.VALID):
        self.parametro = parametro
        self.tipo = tipo
        self.valor = valor
        self.ttl = ttl
        self.prioridade = prioridade
        self.origem = origem
        self.tempo_em_cache = tempo_em_cache
        self.status = status

    def get_entry_as_line(self):
        value = f"{self.parametro} {self.tipo} {self.valor}"
        if self.ttl != "":
            value += f" {self.ttl}"

        if self.prioridade != "":
            value += f" {self.prioridade}"

        return value

    def __str__(self):
        return f"CacheEntry(parametro={self.parametro}, tipo={self.tipo}, valor={self.valor}, ttl={self.ttl}, prioridade={self.prioridade}, origem={self.origem}, tempo_em_cache={self.tempo_em_cache}, status={self.status})"

    def is_free(self) -> bool:
        return self.status == Status.FREE

    def set_free(self) -> None:
        self.status = Status.FREE


class DatabaseConfig:
    def __init__(self, infos: list[CacheEntry] = []):
        self.infos = infos
        self.domain_lines: dict[str, list[int]] = {}

    def has_type_for_domain(self, domain: str, type: str) -> bool:
        for entry in self.infos:
            if entry.parametro == domain and entry.tipo == type:
                return True
        
        return False

    def has_domain(self, domain: str) -> bool: 
        for entry in self.infos:
            if entry.parametro == domain:
                return True
        return False

    def add_entry(self, entry: CacheEntry, domain: str):
        free_cell = -1
        for (index, cell) in enumerate(self.infos):
            if cell.is_free():
                free_cell = index
                break

        if domain not in self.domain_lines:
            self.domain_lines[domain] = []

        if free_cell == -1:
            self.infos.append(entry)
            self.domain_lines[domain].append(len(self.infos) - 1)
        else:
            self.infos[free_cell] = entry 
            self.domain_lines[domain].append(free_cell)
        # self.infos.append(entry)

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
            if (entry.parametro == query_value and entry.tipo == query_type and not entry.is_free()):
                res.append(entry)
            elif query_value == entry.parametro and entry.tipo == "NS" and not entry.is_free():
                auths.append(entry)

        for value in res:
            for entry in self.infos:
                if value.valor == entry.parametro and entry.tipo == "A" and not entry.is_free():
                    ips.append(entry)

        for value in auths:
            for entry in self.infos:
                if value.valor == entry.parametro and entry.tipo == "A" and not entry.is_free():
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
        

    def __clean_domain_db__(self, domain):
        if domain in self.domain_lines:
            for line in self.domain_lines[domain]:
                self.infos[line].set_free()
            

    def read_config_file(self, database_file: list[str], origin: Origin, domain: str):

        self.__clean_domain_db__(domain)

        default = {}

        concatable_value = ""
        for line in filter(lambda x: x[0] != '#', database_file):
            for (variable, value) in default.items():
                line = line.replace(variable, value)

            camps = line.split(' ')
            type = camps[1]
            ttl = ""
            priority = ""

            tam = len(camps)

            if tam > 3:
                ttl = camps[3]

            if tam > 4:
                priority = camps[4]

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
            self.add_entry(CacheEntry(parametro=param, tipo=type, valor=value, ttl=ttl, prioridade=priority, origem=origin, tempo_em_cache=0, status=Status.VALID), domain)






