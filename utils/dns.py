class DNSMessage:
    def __init__(self, id, query_info, values = [], number_extra_values = 0, number_authorities = 0, number_values = 0, flags = [0, 0, 0], response_code = 0, debug_mode = False):
        self.id = id
        self.query_info = query_info
        self.values = values
        self.number_extra_values = number_extra_values
        self.number_authorities = number_authorities
        self.number_values = number_values
        self.flags = flags
        self.response_code = response_code
        self.debug_mode = debug_mode

    def get_values(self):
        values = ""

        if self.number_values != 0:
            for i in range(0, self.number_values):
                values += f"RESPONSE-VALUES = {self.values[i]}\n" 
        else:
            values += "RESPONSE-VALUES = (Null);\n"
        if self.number_authorities != 0:
            for i in range(self.number_values, self.number_authorities):
                values += f"AUTHORITIES-VALUES = {self.values[i]}\n"
        else:
                values += f"AUTHORITIES-VALUES = (Null);\n"
        if self.number_extra_values != 0:
            for i in range(self.number_values + self.number_authorities, self.number_extra_values):
                values += f"EXTRA-VALUES = {self.values[i]}\n"
        else:
            values += "EXTRA-VALUES = (Null);\n"
        return values
            
        

    def to_message_str(self):

        return f"""
# Header
MESSAGE-ID = {self.id}, FLAGS = Q+R, RESPONSE-CODE = {self.response_code},
N-VALUES = {self.number_values}, N-AUTHORITIES = {self.number_authorities}, N-EXTRA-VALUES = {self.number_extra_values},; # Data: Query Info
# Data: Query Info
QUERY-INFO.NAME = {self.query_info[0]}, QUERY-INFO.TYPE = {self.query_info[1]},; # Data: List of Response, Authorities and Extra Values 
# Data: List of Response, Authorities and Extra Values
{self.get_values()}
        """
         
