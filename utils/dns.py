class DNSMessage:
    def __init__(self, id: int, query_info: tuple[str, str], flags: str, values: list[str] = [], number_extra_values: int = 0, number_authorities: int = 0, number_values: int = 0, response_code: int = 0):
        self.id = id
        self.query_info = query_info
        self.__divide_all_values__(values, number_values, number_extra_values, number_authorities)
        self.number_values = number_values
        self.number_extra_values = number_extra_values
        self.number_authorities = number_authorities
        self.flags = flags_from_str(flags)
        self.response_code = response_code

    def __divide_all_values__(self, values: list[str], number_values: int, number_extra_values, number_authorities: int):

        ans_values = []
        auth_values = []
        extra_values = []
        for i in range(number_values):
            ans_values.append(values[i])

        for i in range(number_values, number_values + number_authorities):
            auth_values.append(values[i])

        for i in range(number_values + number_authorities, number_values + number_authorities + number_extra_values):
            extra_values.append(values[i])


        self.response_values = ans_values
        self.auth_values = auth_values
        self.extra_values = extra_values

    def get_id(self) -> int:
        return self.id
            
    def __get__str__from__flags(self):
        camps = []
        if self.flags[0] == 1:
            camps.append('Q')

        if self.flags[1] == 1:
            camps.append('R')

        if self.flags[2] == 1:
            camps.append('A')

        return '+'.join(camps)

    def encode(self) -> bytes:
        id_encode = self.id.to_bytes(2, 'little', signed=False)
        number_values_bytes = self.number_values.to_bytes(1, 'little')
        number_authorities_values_bytes = self.number_authorities.to_bytes(1, 'little')
        number_extra_values_bytes = self.number_extra_values.to_bytes(1, 'little')

        return id_encode

    def get_query_info(self) -> tuple[str, str]:
        return self.query_info
        
    def __str__(self):
        return self.to_message_str()

    def __get_values_str__(self, debug_mode = False):
        values = ""
        number_values = self.number_values
        num_auth_values = self.number_authorities
        num_extra_values = self.number_extra_values
        pre_res_values = ""
        pre_auth_values = ""
        pre_extra_values = ""
        if not debug_mode:
            pre_res_values = "RESPONSE-VALUES = "
            pre_auth_values = "AUTHORITIES-VALUES = "
            pre_extra_values = "EXTRA-VALUES = "
            if number_values == 0:
                values += "RESPONSE-VALUES = (Null)"
            if num_auth_values == 0:
                values += "\nAUTHORITIES-VALUES = (Null)"
            if num_extra_values == 0:
                values += "\nEXTRA-VALUES = (Null)"

        for (i, value) in enumerate(self.response_values):
            if not debug_mode:
                values += '\n'
            values += f"{pre_res_values}{value}" 
            if i == number_values - 1:
                values += ";"
            else:
                values += ","
        for (i, value) in enumerate(self.auth_values):
            if not debug_mode:
                value += '\n'
            values += f"{pre_auth_values}{value}"
            if i == num_auth_values - 1:
                values += ";"
            else:
                values += ","
        for (i, value) in enumerate(self.extra_values):
            if not debug_mode:
                value += '\n'
            values += f"{pre_extra_values}{value}"
            if i == num_extra_values - 1:
                values += ";"
            else:
                values += ","
        return values
            
 
    def to_message_str(self, debug_mode = True):

        if not debug_mode:
            return f"""# Header
MESSAGE-ID = {self.id}, FLAGS = {self.__get__str__from__flags()}, RESPONSE-CODE = {self.response_code},
N-VALUES = {self.number_values}, N-AUTHORITIES = {self.number_authorities}, N-EXTRA-VALUES = {self.number_extra_values},; # Data: Query Info
# Data: Query Info
QUERY-INFO.NAME = {self.query_info[0]}, QUERY-INFO.TYPE = {self.query_info[1]},; # Data: List of Response, Authorities and Extra Values 
# Data: List of Response, Authorities and Extra Values
{self.__get_values_str__()}"""
        else:
            return f"""{self.id},{self.__get__str__from__flags()},{self.response_code},{self.number_values},{self.number_authorities},{self.number_extra_values};{self.query_info[0]},{self.query_info[1]};{self.__get_values_str__(debug_mode)}"""

def flags_from_str(flags: str) -> list[int]:
    flags_list = [0, 0, 0]
    camps = flags.split('+')
    flags_list[0] = int(any(camp == 'Q' for camp in camps))
    flags_list[1] = int(any(camp == 'R' for camp in camps))
    flags_list[2] = int(any(camp == 'A' for camp in camps))

    return flags_list
         
def from_message_str(message: str) -> DNSMessage:
    camps = message.split(';')
    header = camps[0]
    query_info = camps[1]
    header_camps = header.split(',')
    message_id = int(header_camps[0])
    flags = header_camps[1]
    response_code = int(header_camps[2])
    n_values = int(header_camps[3])
    number_authorities = int(header_camps[4])
    number_extra_values = int(header_camps[5])

    query_info_camps = query_info.split(',') 
    query_info_name = query_info_camps[0]
    query_info_type = query_info_camps[1]

    values = []

    index_values_types = 2
    if n_values != 0:
        res_values = camps[index_values_types].split(',')
        for i in range(n_values):
            values.append(res_values[i].lstrip())
        index_values_types += 1

    if number_authorities != 0:
        auth_values = camps[index_values_types].split(',')
        for i in range(number_authorities):
            values.append(auth_values[i].lstrip())
        index_values_types += 1

    if number_extra_values != 0:
        extra_values = camps[index_values_types].split(',')
        for i in range(number_extra_values):
            values.append(extra_values[i].lstrip())
        index_values_types += 1


    message_object = DNSMessage(id=message_id, query_info=(query_info_name, query_info_type), flags=flags, response_code=response_code, values= values, number_extra_values=number_extra_values, number_authorities=number_authorities, number_values=n_values)

    return message_object



def decode_message_dns(message: bytes) -> DNSMessage:
    pass
