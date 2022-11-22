class SameDomainSPSSexception(Exception):
    def __init__(self, message="A server can't be SP and SS for the same domain"):
        self.message = message
        super().__init__(self.message)

class NonSPSSServerLogFileException(Exception):
    def __init__(self, message="A server can't have a log file for a domain which is not SP or SS"):
        self.message = message
        super().__init__(self.message)

class AllLogFileNotReceivedException(Exception):
    def __init__(self, message="You need to determine a file for log file with param all"):
        self.message = message
        super().__init__(message)
