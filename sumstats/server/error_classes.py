
class APIException(Exception):
    def __init__(self):
        super().__init__()


class ArgumentMissing(APIException):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__()
        if message is None:
            message = "Required argument is missing"
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'message': "Bad request. " + self.message}


class InvalidUrl(APIException):
    status_code = 400

    def __init__(self, message=None, status_code=None):
        super().__init__()
        if message is None:
            message = "Invalid URL Syntax"
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'message': "Bad request. " + self.message}


class RequestedNotFound(APIException):
    status_code = 404

    def __init__(self, message=None, status_code=None):
        super().__init__()
        if message is None:
            message = "Item requested not found"
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}