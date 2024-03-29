from enum import Enum
from threading import RLock, Timer

class Status(Enum):
    FREE = 0
    VALID = 1

class Origin(Enum):
    FILE = 0
    SP = 1
    OTHER = 2

class CacheEntry:
    def __init__(self, parametro: str = "", tipo: str = "", valor: str = "", ttl: str = "", prioridade: str = "", origem: Origin = Origin.OTHER, status: Status = Status.VALID):
        self.parametro = parametro
        self.tipo = tipo
        self.valor = valor
        self.ttl = ttl
        self.prioridade = prioridade
        self.origem = origem
        self.status = status

    def get_entry_as_line(self):
        value = f"{self.parametro} {self.tipo} {self.valor}"
        if self.ttl != "":
            value += f" {self.ttl}"

        if self.prioridade != "":
            value += f" {self.prioridade}"

        return value

    def __str__(self):
        return f"CacheEntry(parametro={self.parametro}, tipo={self.tipo}, valor={self.valor}, ttl={self.ttl}, prioridade={self.prioridade}, origem={self.origem}, status={self.status})"

    def is_free(self) -> bool:
        return self.status == Status.FREE

    def set_free(self) -> None:
        self.status = Status.FREE


def cache_entry_from_str(message: str, origem: Origin) -> CacheEntry:
    camps = message.split(' ')
    parametro = camps[0]
    tipo = camps[1]
    valor = camps[2]
    ttl = "" if len(camps) < 4 else camps[3]
    prioridade = "" if len(camps) < 5 else camps[4]
    return CacheEntry(parametro=parametro, tipo=tipo, valor=valor, ttl=ttl, prioridade=prioridade, origem=origem)
        

class CacheConfig:
    def __init__(self, infos: list[CacheEntry] = []):
        self.lock = RLock()
        self.infos = infos
        self.ss_domain_lines: dict[str, set[int]] = {}
        self.clean_ss_lines: dict[str, Timer] = {}

    def __free_line__(self, line: int):
        with self.lock:
            if len(self.infos) > line:
                self.infos[line].set_free()

    def has_type_for_domain(self, domain: str, type: str) -> bool:
        with self.lock:
            for entry in self.infos:
                if entry.parametro == domain and entry.tipo == type:
                    return True
            return False
        
    def has_domain(self, domain: str) -> bool: 
        with self.lock:
            for entry in self.infos:
                if entry.parametro == domain:
                    return True
            return False

    def add_entry(self, entry: CacheEntry, domain: str = ""):
        with self.lock:
            free_cell = -1
            for (index, cell) in enumerate(self.infos):
                if cell.is_free():
                    free_cell = index
                    break

            if domain != "" and domain not in self.ss_domain_lines:
                self.ss_domain_lines[domain] = set()

            if free_cell == -1:
                free_cell = len(self.infos)
                self.infos.append(entry)
                if domain != "":
                    self.ss_domain_lines[domain].add(len(self.infos) - 1)
            else:
                self.infos[free_cell] = entry 
                if domain != "":
                    self.ss_domain_lines[domain].add(free_cell)

            if entry.origem == Origin.OTHER:
                Timer(0 if entry.ttl == "" else int(entry.ttl), self.clean_entry, [free_cell]).start()

    def clean_entry(self, index: int):
        with self.lock:
            if index < len(self.infos):
                print(self.infos[index])
                self.infos[index].set_free()
                print(self.infos[index])

    def __str__(self):
        with self.lock:
            string = "DatabaseConfig("
            for inf in self.infos:
                string += inf.__str__() + ", \n"

            string +=");"
            return string;
            

    def get_cache_values(self, query_value, query_type) -> tuple[list[str], list[str], list[str]]:
        with self.lock:
            res: list[CacheEntry] = []
            auths: list[CacheEntry]= []
            ips: set[CacheEntry] = set()

            for entry in self.infos:
                if (entry.parametro == query_value and entry.tipo == query_type and not entry.is_free()):
                    res.append(entry)
                if query_value == entry.parametro and entry.tipo == "NS" and not entry.is_free():
                    auths.append(entry)

            for value in res:
                for entry in self.infos:
                    if value.valor == entry.parametro and entry.tipo == "A" and not entry.is_free():
                        ips.add(entry)

            for value in auths:
                for entry in self.infos:
                    if value.valor == entry.parametro and entry.tipo == "A" and not entry.is_free() and entry not in ips:
                        ips.add(entry)

            res_str = list(map(lambda entry: entry.get_entry_as_line(), res))
            auths_str = list(map(lambda entry: entry.get_entry_as_line(), auths))
            ips_str = list(map(lambda entry: entry.get_entry_as_line(), ips))

            return(res_str, auths_str, ips_str)

    def __concat_default_value__(self, words: list[str], concat_value: str) -> list[str]:
        if concat_value == "":
            return words

        if words[0][-1] != '.':
            words[0] += '.' + concat_value

        # if not words[2].isdigit() and not self.__is_an_ip__(words[2]) and words[2][-1] != '.':
        #     words[2] += '.' + concat_value
            
        return words
            

    def __is_an_ip__(self, value: str) -> bool:
        camps = value.split('.')
        return len(camps) == 4 and all(camp.isdigit() for camp in camps)
        

    def add_expire_ss_timer(self, domain: str, expire_time: int):
        if domain in self.clean_ss_lines:
            self.clean_ss_lines[domain].cancel()

        self.clean_ss_lines[domain] = Timer(expire_time, self.__clean_domain_db__, [domain])
        self.clean_ss_lines[domain].start()

    def __clean_domain_db__(self, domain: str):
        with self.lock:
            if domain in self.ss_domain_lines:
                for line in self.ss_domain_lines[domain]:
                    self.infos[line].set_free()

                self.ss_domain_lines[domain].clear()

    def get_closer_domain_with_auth(self, domain: str) -> str | None:
        with self.lock:
            while domain:
                res = set(filter(lambda entry: entry.tipo == "NS" and entry.parametro == domain and entry.status == Status.VALID, self.infos))
                if len(res) != 0:
                    print(domain)
                    return domain
                domain = domain.split('.', maxsplit=1)[1]

            return None
            

    def read_database_file(self, database_file: list[str], origin: Origin, domain: str):
        if origin == Origin.SP:
            self.__clean_domain_db__(domain)

        default = {}

        concatable_value = ""
        for line in filter(lambda x: x and x[0] != '#', database_file):
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

            param = camps[0]
            value = camps[2]
            if type == "DEFAULT":
                if param not in default:
                    default[param] = value
                    if param == "@":
                        concatable_value = value
            self.add_entry(CacheEntry(parametro=param, tipo=type, valor=value, ttl=ttl, prioridade=priority, origem=origin, status=Status.VALID), domain)


        






