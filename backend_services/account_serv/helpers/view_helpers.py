from http import HTTPStatus

from rest_framework.response import Response

from models.error_response import ErrorResponse


def check_error_response_instance(data):
    return isinstance(data, ErrorResponse)


def error_response(data, status_code=HTTPStatus.BAD_REQUEST):
    return Response(status=status_code, exception=True, data=data)


def success_response(data, status_code=HTTPStatus.OK):
    return Response(status=status_code, data=data)
