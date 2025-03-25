import logging

from django.http import Http404
from rest_framework import serializers
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .responses import error_response

logger = logging.getLogger(__name__)


def custom_exception_handler(exception, context) -> Response | None:
    if not isinstance(exception, serializers.ValidationError | Http404 | PermissionDenied):
        logger.exception(
            'An exception occurred while handling request %s',
            context['request'].get_full_path(),
            exc_info=exception,
        )

    response = exception_handler(exception, context)
    if response is None:
        return None

    if isinstance(exception, APIException):
        if isinstance(exception.detail, dict):
            error_message = ' '.join([f'{key}: {value[0]}' for key, value in exception.detail.items()])
        elif isinstance(exception.detail, list):
            error_message = ' '.join([str(item) for item in exception.detail])
        else:
            error_message = str(exception.detail)

        return error_response(
            error=error_message,
            status_code=response.status_code,
        )

    return error_response(error=str(exception), status_code=response.status_code)
