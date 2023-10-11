from fastapi import status, Response, HTTPException
from fastapi.encoders import jsonable_encoder

from src.schemas.error_response import ErrorResponse


def check_error_response_instance(data):
    return isinstance(data, ErrorResponse)


def route_error_response(detail, status_code=status.HTTP_400_BAD_REQUEST):
    return HTTPException(status_code=status_code, detail=jsonable_encoder(detail))


def route_success_response(content, status_code=status.HTTP_200_OK):
    return Response(status_code=status_code, content=jsonable_encoder(content))
