class DNSMessage:
    def __init__(self, id: int, query_info: tuple[str, str], flags: str, values: list[str] = [], number_extra_values: int = 0, number_authorities: int = 0, number_values: int = 0, response_code: int = 0):
        self.id = id
        self.query_info = query_info
        self.values = values
        self.number_extra_values = number_extra_values
        self.number_authorities = number_authorities
        self.number_values = number_values
        self.flags = flags
        self.response_code = response_code

    def get_query_info(self) -> tuple[str, str]:
        return self.query_info
        
    def __str__(self):
        return self.to_message_str()

    def __get_values__(self, debug_mode = False):
        values = ""

        if not debug_mode:
            if self.number_values != 0:
                for i in range(0, self.number_values):
                    values += f"RESPONSE-VALUES = {self.values[i]}" 
                    if i == self.number_values - 1:
                        values += ";\n"
                    else:
                        values += ",\n"
            else:
                values += "RESPONSE-VALUES = (Null)\n"
            if self.number_authorities != 0:
                for i in range(self.number_values, self.number_authorities):
                    values += f"AUTHORITIES-VALUES = {self.values[i]},"
                    if i == self.number_authorities - 1:
                        values += ";\n"
                    else:
                        values += "\n"
            else:
                values += f"AUTHORITIES-VALUES = (Null)\n"
            if self.number_extra_values != 0:
                for i in range(self.number_values + self.number_authorities, self.number_extra_values):
                    values += f"EXTRA-VALUES = {self.values[i]},\n"
                    if i == self.number_extra_values - 1:
                        values += ";\n"
                    else:
                        values += "\n"
            else:
                values += "EXTRA-VALUES = (Null)"
            return values
        else:
            for i in range(self.number_values):
                values += self.values[i]
                if i == self.number_values - 1:
                    values += ";\n"   
                else:
                    values += ",\n"
            for i in range(self.number_authorities):
                values += self.values[i]
                if i == self.number_values - 1:
                    values += ";\n"   
                else:
                    values += ",\n"
            for i in range(self.number_values):
                values += self.values[i]
                if i == self.number_values - 1:
                    values += ";\n"   
                else:
                    values += ",\n"
            
    
    def decode_message(self):
        #TODO
        pass
 
    def to_message_str(self, debug_mode = False):

        if not debug_mode:
            return f"""# Header
MESSAGE-ID = {self.id}, FLAGS = {self.flags}, RESPONSE-CODE = {self.response_code},
N-VALUES = {self.number_values}, N-AUTHORITIES = {self.number_authorities}, N-EXTRA-VALUES = {self.number_extra_values},; # Data: Query Info
# Data: Query Info
QUERY-INFO.NAME = {self.query_info[0]}, QUERY-INFO.TYPE = {self.query_info[1]},; # Data: List of Response, Authorities and Extra Values 
# Data: List of Response, Authorities and Extra Values
{self.__get_values__()}"""
        else:
            return f"""{self.id},{self.flags},{self.response_code},{self.number_values},{self.number_authorities},{self.number_extra_values};{self.query_info[0]},{self.query_info[1]};"""
         
def from_message_str(message: str):
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
        values = camps[index_values_types].split(',')
        for i in range(n_values):
            values.append(values[i])
        index_values_types += 1

    if number_authorities != 0:
        values = camps[index_values_types].split(',')
        for i in range(number_authorities):
            values.append(values[i])
        index_values_types += 1

    if number_extra_values != 0:
        values = camps[index_values_types].split(',')
        for i in range(number_extra_values):
            values.append(values[i])
        index_values_types += 1

    message_object = DNSMessage(id=message_id, query_info=(query_info_name, query_info_type), flags=flags, response_code=response_code, values= values, number_extra_values=number_extra_values, number_authorities=number_authorities, number_values=n_values)

    return message_object

