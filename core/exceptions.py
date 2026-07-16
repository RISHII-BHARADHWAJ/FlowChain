"""
Custom exception handler for the SCM platform
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('scm')


def custom_exception_handler(exc, context):
    """Custom exception handler that returns structured error responses"""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': _get_error_message(response),
                'details': response.data,
            }
        }
        response.data = custom_response_data
    else:
        # Unhandled exception
        logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={
            'view': context.get('view'),
            'request': context.get('request'),
        })
        response = Response({
            'success': False,
            'error': {
                'code': 500,
                'message': 'An internal server error occurred.',
                'details': str(exc) if __debug__ else 'Internal Server Error',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def _get_error_message(response):
    """Extract a user-friendly error message from the response"""
    status_code = response.status_code
    messages = {
        400: 'Bad request. Please check your input.',
        401: 'Authentication required. Please log in.',
        403: 'You do not have permission to perform this action.',
        404: 'The requested resource was not found.',
        405: 'Method not allowed.',
        429: 'Too many requests. Please slow down.',
        500: 'Internal server error.',
    }
    return messages.get(status_code, 'An error occurred.')
