from rest_framework import status
from rest_framework.exceptions import APIException


class GenericException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    code = 1000
    summary = 'Error'
    verbose = False

    def __init__(self, message=None, status_code=400):
        if not message:
            message = 'We hit a snag. Please check your internet connection and try'
        if status:
            self.status_code = status_code
        super().__init__(message)

    def serialize(self):
        return {
            'code': self.code,
            'message': self.detail,
            'summary': self.summary
        }


class InvalidParamId(GenericException):
    code = 1004

    def __init__(self, message=None):
        if not message:
            message = 'invalid param id'
        super().__init__(message)


class InvalidFilterException(GenericException):
    code = 1005

    def __init__(self, message=None):
        if not message:
            message = 'invalid filter'
        super(InvalidFilterException, self).__init__(message)
