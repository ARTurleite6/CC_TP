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
            

    def encode(self) -> bytes | None:
        id_encode = self.id.to_bytes(2, 'big', signed=False)
        number_values_bytes = self.number_values.to_bytes(1, 'big', signed=False)
        number_authorities_values_bytes = self.number_authorities.to_bytes(1, 'big', signed=False)
        number_extra_values_bytes = self.number_extra_values.to_bytes(1, 'big', signed=False)
        response_flags = 0

        if self.flags[0] == 1:
            response_flags |= 0b00010000
        if self.flags[1] == 1:
            response_flags |= 0b00001000
        if self.flags[2] == 1:
            response_flags |= 0b00000100

        response_flags |= self.response_code
        response_flags = response_flags.to_bytes(1, 'big', signed=False)
        query_name_length = len(self.query_info[0]).to_bytes(1, 'big', signed=False)
        query_name_encode = self.query_info[0].encode('ascii')
        query_type_encode = encode_type_query_info(self.query_info[1])

        if query_type_encode is None:
            return None
        query_type_encode = query_type_encode.to_bytes(1, 'big', signed=False)

        values = bytes()
        for value in self.response_values:
            value_encode = encode_value(value)
            if value_encode is None:
                return None
            values += value_encode
        for value in self.auth_values:
            value_encode = encode_value(value)
            if value_encode is None:
                return None
            values += value_encode
        for value in self.extra_values:
            value_encode = encode_value(value)
            if value_encode is None:
                return None
            values += value_encode
            

        return id_encode + response_flags + number_values_bytes + number_authorities_values_bytes + number_extra_values_bytes + query_name_length + query_name_encode + query_type_encode + len(values).to_bytes(1, 'big', signed=False) + values

    def get_query_info(self) -> tuple[str, str]:
        return self.query_info
        
    def __str__(self):
        return self.to_message_str(debug_mode=False)

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

        for (i, value) in enumerate(self.response_values):
            if not debug_mode:
                values += '\n'
            values += f"{pre_res_values}{value}" 
            if i == number_values - 1:
                values += ";"
            else:
                values += ","

        if num_auth_values == 0:
            values += "\nAUTHORITIES-VALUES = (Null)"
        for (i, value) in enumerate(self.auth_values):
            if not debug_mode:
                values += '\n'
            values += f"{pre_auth_values}{value}"
            if i == num_auth_values - 1:
                values += ";"
            else:
                values += ","
        if num_extra_values == 0:
            values += "\nEXTRA-VALUES = (Null)"
        for (i, value) in enumerate(self.extra_values):
            if not debug_mode:
                values += '\n'
            values += f"{pre_extra_values}{value}"
            if i == num_extra_values - 1:
                values += ";"
            else:
                values += ","
        return values
            
 
    def to_message_str(self, debug_mode = True):

        if not debug_mode:
            return f"""# Header
MESSAGE-ID = {self.id}, FLAGS = {get_str_from_flags(self.flags)}, RESPONSE-CODE = {self.response_code},
N-VALUES = {self.number_values}, N-AUTHORITIES = {self.number_authorities}, N-EXTRA-VALUES = {self.number_extra_values},;
# Data: Query Info
QUERY-INFO.NAME = {self.query_info[0]}, QUERY-INFO.TYPE = {self.query_info[1]},;
# Data: List of Response, Authorities and Extra Values
{self.__get_values_str__()}"""
        else:
            return f"""{self.id},{get_str_from_flags(self.flags)},{self.response_code},{self.number_values},{self.number_authorities},{self.number_extra_values};{self.query_info[0]},{self.query_info[1]};{self.__get_values_str__(debug_mode)}"""

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

def decode_type_query_info(byte: int) -> str | None:
    if byte == 0b00000000:
        return "DEFAULT"
    elif byte == 0b00000001:
        return "SOASP"
    elif byte == 0b00000010:
        return "SOAADMIN"
    elif byte == 0b00000011:
        return "SOASERIAL"
    elif byte == 0b00000100:
        return "SOAREFRESH"
    elif byte == 0b00000101:
        return "SOARETRY"
    elif byte == 0b00000110:
        return "SOAEXPIRE"
    elif byte == 0b00000111:
        return "NS"
    elif byte == 0b00001000:
        return "A"
    elif byte == 0b00001001:
        return "CNAME"
    elif byte == 0b00001010:
        return "MX"
    elif byte == 0b00001011:
        return "PTR"
    else:
        return None

def get_str_from_flags(flags: list[int]) -> str:
    camps = []
    if flags[0] == 1:
        camps.append('Q')
    if flags[1] == 1:
        camps.append('R')
    if flags[2] == 1:
        camps.append('A')
    return '+'.join(camps)

def decode_string(string: bytes, start: int, end: int) -> str:
    res = ""
    for index in range(start, end):
        res += chr(string[index])
    return res

def decode_message_dns(message: bytes) -> DNSMessage | None:
    message_id = message[0] + message[1]
    response_flags = message[2]
    flags = []
    flags.append(1 if 0b00010000 & response_flags != 0 else 0)
    flags.append(1 if 0b00001000 & response_flags != 0 else 0)
    flags.append(1 if 0b00000100 & response_flags != 0 else 0)
        # return id_encode + response_flags + number_values_bytes + number_authorities_values_bytes + number_extra_values_bytes + query_name_length + query_name_encode + query_type_encode + values
    response_code = response_flags & 0b00000011
    number_values = message[3]
    print("number_values =", number_values)
    number_auth_values = message[4]
    print("number_auth_values =", number_auth_values)
    number_extra_values = message[5]
    print("number_extra_values =", number_extra_values)
    query_name_length = message[6]
    query_name = decode_string(message, 6 + 1, 6 + 1 + query_name_length)
    type = message[6 + 1 + query_name_length]
    type = decode_type_query_info(type)
    if type is None:
        return None

    values = []
    len_values = message[8 + query_name_length] + message[9 + query_name_length] + message[10 + query_name_length] + message[11 + query_name_length]
    index = 12 + query_name_length
    value_index = 1
    while index < 12 + query_name_length + len_values:
        dom_length = message[index]
        print("dom_length=", dom_length)
        index += 1
        dom = decode_string(message, index, index + dom_length)
        print("dom=", dom)
        index += dom_length
        type_value = message[index]
        print("type_value=", type_value)
        index += 1
        param_length = message[index]
        print("param_legnth=", param_length)
        index += 1
        param = decode_string(message, index, index + param_length)
        print("param=", param)
        index += param_length
        res = dom
        has_ttl = False
        has_priority = False
        if type_value & 0b00010000 != 0:
            has_ttl = True
            type_value &= 0b11101111
        if type_value & 0b00100000 != 0:
            has_priority = True
            type_value &= 0b11011111
        print(type_value, "value=", value_index)
        type_decode = decode_type_query_info(type_value)
        if type_decode is None:
            print("deu erro qui")
            return None
        res += type_decode + param
        if has_ttl:
            res += str(message[index] + message[index + 1] + message[index + 2] + message[index + 3])
            index += 4
        if has_priority:
            res += str(message[index])
            index += 1 
            
        value_index += 1
        values.append(res)

    return DNSMessage(id=message_id, response_code=response_code, flags=(get_str_from_flags(flags)), number_values=number_values, number_authorities=number_auth_values, number_extra_values=number_extra_values, query_info=(query_name, type))

def encode_type_query_info(type: str) -> int | None:
    value = -1
    if type == "DEFAULT":
        value = 0b00000000
    elif type == "SOASP":
        value = 0b00000001
    elif type == "SOAADMIN":
        value = 0b00000010
    elif type == "SOASERIAL":
        value = 0b00000011
    elif type == "SOAREFRESH":
        value = 0b00000100
    elif type == "SOARETRY":
        value = 0b00000101
    elif type == "SOAEXPIRE":
        value = 0b00000110
    elif type == "NS":
        value = 0b00000111
    elif type == "A":
        value = 0b00001000
    elif type == "CNAME":
        value = 0b00001001
    elif type == "MX":
        value = 0b00001010
    elif type == "PTR":
        value = 0b00001011
    if value == -1:
        return None
    return value

def encode_value(value: str) -> bytes | None:
    camps = value.split(' ') 
    parameter = camps[0]
    type = camps[1]
    value_camp = camps[2]
    ttl = "" if len(camps) <= 3 else camps[3]
    priority = "" if len(camps) <= 4 else camps[4]
    parameter_length = len(parameter).to_bytes(1, 'big', signed=False)
    parameter = parameter.encode('ascii')
    type = encode_type_query_info(type)
    if type is None:
        return None
    value_length = len(value_camp).to_bytes(1, 'big', signed=False)
    value_camp = value_camp.encode('ascii')
    if ttl != "":
        type |= 0b00010000
    if priority != "":
        type |= 0b00100000
    res = parameter_length + parameter + type.to_bytes(1, 'big', signed=False) + value_length + value_camp 
    if ttl != "":
        res += int(ttl).to_bytes(4, 'big', signed=False)
    if priority != "":
        res += int(priority).to_bytes(1, 'big', signed=False)
    return res

