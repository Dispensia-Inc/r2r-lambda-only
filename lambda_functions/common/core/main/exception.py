import json


class LambdaException(Exception):
    def __init__(self, error_msg: str, status_code: int):
        self.status_code = status_code
        self.error_msg = error_msg

    def __str__(self):
        obj = {
            "statusCode": self.status_code,
            "errorMessage": self.error_msg
        }
        return json.dumps(obj)
