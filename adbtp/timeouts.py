"""
    adbtp.timeouts
    ~~~~~~~~~~~~~~

    Contains functionality for dealing with protocol timeouts.
"""
import functools
import time

import adbts

from . import exceptions, hints

__all__ = ['Timeout', 'wrap']

#: Sentinel object used to indicate when a timeout value was actually passed
#: since `None` is a valid type.
#: Note: This needs to match the sentinel value in the `adbts` package so the value can be passed down.
UNDEFINED = adbts.timeouts.UNDEFINED


#: Number of additional milliseconds to spend if a timeout expires between sending header and message.
OVERAGE = 100


def ensure_started(func):
    """
    Decorator used to guard :class:`~adbtp.timeouts.Timeout` methods that require it to be started.
    """
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):  # pylint: disable=missing-docstring
        if not self.started:
            raise exceptions.TimeoutNotStartedError(
                'Action "{}" requires timeout to be started'.format(func.__name__))
        return func(self, *args, **kwargs)
    return decorator


class Timeout:
    """
    Defines a duration of time tracked by context manager.
    """

    def __init__(self, period: hints.Timeout) -> None:
        """
        Create a new :class:`~adbtp.timeouts.Timeout` instance.

        :param period: Timeout duration in seconds
        :type period: :class:`~int` or :class:`~object`
        """
        self._period = period
        self._start_time = None
        self._stop_time = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __repr__(self) -> hints.Str:
        return '<{}({!r})>'.format(self.__class__.__name__, str(self))

    def __str__(self) -> hints.Str:
        return 'undefined' if self.undefined else '{} seconds'.format(self.period)

    @property
    def undefined(self):
        """
        Check to see if period of time is logically undefined.

        This means that the timeout represents the "sentinel" value. This value indicates that the
        caller did not specify any specific timeout value and it should use the transport specific
        default timeout value.

        :return: Check to see if this timeout has an undefined period
        :rtype: :class:`~bool`
        """
        return self.period is UNDEFINED

    @property
    def period(self) -> hints.Timeout:
        """
        Length of time in seconds of this timeout.

        :return: The period of time for the timeout
        :rtype: :class:`~int` or :class:`~object`
        """
        return self._period

    @property
    def started(self) -> hints.Bool:
        """
        Check to see if timeout has started running.

        :return: Boolean indicating whether or not timeout has been started
        :rtype: :class:`~bool`
        """
        return self._start_time is not None

    @property
    def stopped(self) -> hints.Bool:
        """
        Check to see if timeout has stopped running.

        :return: Boolean indicating whether or not timeout has been stopped
        :rtype: :class:`~bool`
        """
        return self._stop_time is not None

    @property
    @ensure_started
    def exceeded(self) -> hints.Bool:
        """
        Check to see if timeout has been running longer than period.

        :return: Boolean indicating whether or not timeout has been running too long
        :rtype: :class:`~bool`
        """
        return False if self.undefined else self.remaining_seconds <= 0

    @property
    @ensure_started
    def elapsed_seconds(self) -> hints.Int:
        """
        Number of seconds since the timeout started.

        :return: Number of seconds since start
        :rtype: :class:`~int`
        """
        return int(self._stop_time or time.time() - self._start_time)

    @property
    @ensure_started
    def elapsed_milliseconds(self) -> hints.Int:
        """
        Number of milliseconds since the timeout started.

        :return: Number of milliseconds since start
        :rtype: :class:`~int`
        """
        return self.elapsed_seconds * 1000

    @property
    @ensure_started
    def remaining_seconds(self) -> hints.Timeout:
        """
        Number of seconds remaining before timeout period is exceeded.

        :return: Number of seconds remaining
        :rtype: :class:`~int` or :class:`~object`
        """
        return self.period if self.undefined else max(0, self.period - self.elapsed_seconds)

    @property
    @ensure_started
    def remaining_milliseconds(self) -> hints.Timeout:
        """
        Number of milliseconds remaining before timeout period is exceeded.

        :return: Number of milliseconds remaining
        :rtype: :class:`~int` or :class:`~object`
        """
        return self.period if self.undefined else self.remaining_seconds * 1000

    def start(self) -> None:
        """
        Start the "timer" for this timeout instance.

        This is called automatically by :meth:`~adbtp.timeouts.timeout.__enter__` when using this
        as a context manager.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        self._start_time = time.time()

    @ensure_started
    def stop(self) -> None:
        """
        Stop the "timer" for this timeout instance.

        This is called automatically by :meth:`~adbtp.timeouts.timeout.__exit__` when using this
        as a context manager.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        self._stop_time = time.time()


def wrap(timeout):
    """
    Wrap the given timeout value in a :class:`~adbtp.timeouts.Timeout` instance.

    If the given timeout value is already a :class:`~adbtp.timeouts.Timeout` instance, it is returned as-is.

    :param timeout: Timeout value to use
    :type timeout: :class:`~int`, :class:`~object`, or :class:`~adbtp.timeouts.Timeout`
    :return: Timeout instance that wraps the given value
    :rtype: :class:`~adbtp.timeouts.Timeout`
    """
    if isinstance(timeout, Timeout):
        return timeout
    if timeout is not UNDEFINED:
        timeout = int(timeout)
    return Timeout(timeout)
