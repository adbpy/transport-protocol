"""
    adbtp.exceptions
    ~~~~~~~~~~~~~~~~

    Contains exception types used across the package.
"""
import functools
import typing

#: Type hint that defines a exception type that derives from :class:`~Exception`.
ExceptionType = typing.TypeVar('ExceptionType', bound=Exception)  # pylint: disable=invalid-name

#: Type hint that defines a collection of one or more exception types
#: that can be caught/raised.
ExceptionTypes = typing.Union[ExceptionType,  # pylint: disable=invalid-name
                              typing.Tuple[ExceptionType, ...]]  # pylint: disable=invalid-sequence-index


class TransportProtocolError(Exception):
    """
    Base exception for all transport protocol related errors.
    """


class TransportProtocolTimeoutError(TransportProtocolError):
    """
    Exception raised when underlying transport call or protocol action exceeds timeout.
    """


class TimeoutNotStartedError(TransportProtocolError):
    """
    Exception raised when attempting to perform certain actions on :class:`~adbtp.timeouts.Timeout` instances
    that have not yet been started.
    """


def reraise(exc_to_catch: ExceptionTypes):
    """
    Decorator that catches specific exception types and re-raises them as
    :class:`~adbtp.exceptions.TransportProtocolError`.

    :param exc_to_catch: Transport specific timeout exception type(s) to catch
    :type exc_to_catch: :class:`~Exception` or :class:`~tuple`
    """
    def decorator(func):  # pylint: disable=missing-docstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # pylint: disable=missing-docstring
            try:
                return func(*args, **kwargs)
            except exc_to_catch as ex:
                raise TransportProtocolError('Transport protocol encountered an error') from ex
        return wrapper
    return decorator


def reraise_timeout_errors(exc_to_catch: None):
    """
    Decorator that catches specific timeout related exceptions and re-raises them as
    :class:`~adbtp.exceptions.TransportProtocolTimeoutError`.

    :param exc_to_catch: Transport specific timeout exception type(s) to catch
    :type exc_to_catch: :class:`~Exception` or :class:`~tuple`
    """
    def decorator(func):  # pylint: disable=missing-docstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # pylint: disable=missing-docstring
            try:
                return func(*args, **kwargs)
            except exc_to_catch as ex:
                raise TransportProtocolTimeoutError(
                    'Exceeded timeout: {}'.format(kwargs.get('timeout'))) from ex
        return wrapper
    return decorator
