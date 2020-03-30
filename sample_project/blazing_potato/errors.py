
class InvalidDIYInputFormat(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class MissingFIeld(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class InvalidKey(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class RedisNotAvailable(Exception):
    def __init__(self, message):
        self.message = message + "\n"

