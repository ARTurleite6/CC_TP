class DNSMessage:
    def __init__(self, id, query_info, extra_values= [], authorities_values = [], response_values = [], number_extra_values = 0, number_authorities = 0, number_values = 0, flags = [0, 0, 0], response_code = 0):
        self.id = id
        self.query_info = query_info
        self.extra_values = extra_values
        self.authorities_values = authorities_values
        self.response_values = response_values
        self.number_extra_values = number_extra_values
        self.number_authorities = number_authorities
        self.number_values = number_values
        self.flags = flags
        self.response_code = response_code

    def get_values(self):
        values = ""
        if self.number_values != 0:
            for value in self.response_values:
                values += f"RESPONSE-VALUES = {value}\n" 
        else:
            values += "RESPONSE-VALUES = (Null)\n"
        if self.number_authorities != 0:
            for value in self.response_values:
                values += f"AUTHORITIES-VALUES = {value}\n"
        else:
                values += f"AUTHORITIES-VALUES = (Null)\n"
        if self.number_extra_values != 0:
            for value in self.response_values:
                values += f"EXTRA-VALUES = {value}\n"
        else:
            values += "EXTRA-VALUES = (Null)\n"
            
        

    def to_message_str(self):

        return f"""
            MESSAGE-ID = {self.id}, FLAGS = Q+R, RESPONSE-CODE = {self.response_code},
            N-VALUES = {self.number_values}, N-AUTHORITIES = {self.number_authorities}, N-EXTRA-VALUES = {self.number_extra_values},; # Data: Query Info
            QUERY-INFO.NAME = {self.query_info[0]}, QUERY-INFO.TYPE = {self.query_info[1]},; # Data: List of Response, Authorities and Extra Values 
            {self.get_values()}
        """
         
