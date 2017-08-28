"""
    adbtp.protocol
    ~~~~~~~~~~~~~~

    Defines abstract base class that all protocols must implement.
"""
import abc
import functools

from . import exceptions, hints, timeouts

__all__ = ['Protocol']


def ensure_opened(func):
    """
    Decorator used to guard :class:`~adbtp.protocol.Protocol` methods that require it not to be closed.
    """
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):  # pylint: disable=missing-docstring
        if self.closed:
            raise exceptions.TransportProtocolClosedError('Cannot perform this action against closed protocol')
        return func(self, *args, **kwargs)
    return decorator


class Protocol(metaclass=abc.ABCMeta):
    """
    Abstract class that defines a transport protocol.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return '<{}({!r})>'.format(self.__class__.__name__, str(self))

    @property
    @abc.abstractmethod
    def closed(self) -> hints.Bool:
        """
        Checks to see if the protocol is closed.

        :return: Closed state of the protocol
        :rtype: :class:`~bool`
        """

    @abc.abstractmethod
    def read(self, timeout: hints.Timeout=timeouts.SENTINEL):
        """
        Read a message from the protocol.

        :param timeout: Maximum number of milliseconds to read before raising an exception
        :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
        :return: A message read from the protocol
        :rtype: :class:`~adbwp.message.Message`
        """

    @abc.abstractmethod
    def write(self, message, timeout: hints.Timeout=timeouts.SENTINEL) -> None:
        """
        Write a message to the protocol.

        :param message: Message to write
        :type message: :class:`~adbwp.message.Message`
        :param timeout: Maximum number of milliseconds to read before raising an exception
        :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
        :return: Nothing
        :rtype: :class:`~NoneType`
        """

    @abc.abstractmethod
    def close(self) -> None:
        """
        Close the protocol.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
