from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    """Возвращает статус-код 400."""
    default_detail = '400 Bad Request'
    default_code = 'bad_request'
    status_code = status.HTTP_400_BAD_REQUEST
