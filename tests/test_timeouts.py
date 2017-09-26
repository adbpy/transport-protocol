"""
    test_timeouts
    ~~~~~~~~~~~~~

    Tests for the :mod:`~adbtp.timeouts` module.
"""
import time

import pytest

from adbtp import exceptions, timeouts


@pytest.fixture(scope='session', params=[
    'exceeded',
    'elapsed_seconds',
    'elapsed_milliseconds',
    'remaining_seconds',
    'remaining_milliseconds'
])
def ensure_started_property_names(request):
    """
    Fixture that yields property names on the :class:`~adbtp.timeouts.Timeout` class that are decorated
    with :func:`~adbtp.timeouts.ensure_started`.
    """
    return request.param


@pytest.fixture(scope='session', params=[
    'stop'
])
def ensure_started_method_names(request):
    """
    Fixture that yields method names on the :class:`~adbtp.timeouts.Timeout` class that are decorated
    with :func:`~adbtp.timeouts.ensure_started`.
    """
    return request.param


@pytest.fixture(scope='session', params=[1, 2, 5, 10, 30])
def valid_period(request):
    """
    Fixture that yields valid timeout periods in seconds.
    """
    return request.param


@pytest.fixture(scope='function')
def not_started_timeout():
    """
    Fixture that yields a :class:`~adbtp.timeouts.Timeout` that has not been started.
    """
    return timeouts.Timeout(1)


@pytest.fixture(scope='session')
def stopped_timeout():
    """
    Fixture that yields a :class:`~adbtp.timeouts.Timeout` that has been started and stopped.
    """
    timeout = timeouts.Timeout(1)
    timeout.start()
    timeout.stop()
    return timeout


@pytest.fixture(scope='function')
def undefined_timeout():
    """
    Fixture that yields a :class:`~adbtp.timeouts.Timeout` that was created using the timeout sentinel value.
    """
    return timeouts.Timeout(timeouts.UNDEFINED)


def test_ensure_started_wrapped_property_raises_on_not_started_timeout(not_started_timeout,
                                                                       ensure_started_property_names):
    """
    Assert that properties decorated with :func:`~adbtp.timeouts.Timeout.ensure_started` raise a
    :class:`~adbtp.exceptions.TimeoutNotStartedError` when the instance hasn't been started.
    """
    with pytest.raises(exceptions.TimeoutNotStartedError):
        getattr(not_started_timeout, ensure_started_property_names)


def test_ensure_started_wrapped_method_raises_on_not_started_timeout(not_started_timeout,
                                                                     ensure_started_method_names):
    """
    Assert that methods decorated with :func:`~adbtp.timeouts.Timeout.ensure_started` raise a
    :class:`~adbtp.exceptions.TimeoutNotStartedError` when the instance hasn't been started.
    """
    with pytest.raises(exceptions.TimeoutNotStartedError):
        getattr(not_started_timeout, ensure_started_method_names)()


def test_undefined_true_when_using_sentinel_value(undefined_timeout):
    """
    Assert that :prop:`~adbtp.timeouts.Timeout.undefined` returns `True` when the timeout was created
    from the sentinel value.
    """
    assert undefined_timeout.undefined is True


def test_period_property_returns_given_value(valid_period):
    """
    Assert that :prop:`~adbtp.timeouts.Timeout.period` returns the given period time value.
    """
    timeout = timeouts.Timeout(valid_period)
    assert timeout.period == valid_period


def test_timeout_started_after_context_manager_enter(not_started_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.started` returns `True` after
    :meth:`~adbts.timeout.Timeout.__enter__` is called.
    """
    with not_started_timeout:
        assert not_started_timeout.started
        assert not not_started_timeout.stopped


def test_timeout_stopped_after_context_manager_exit(not_started_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.stopped` returns `True` after
    :meth:`~adbts.timeout.Timeout.__exit__` is called.
    """
    with not_started_timeout:
        assert not not_started_timeout.stopped
    assert not_started_timeout.stopped


def test_timeout_exceeded_when_elapsed_greater_than_period():
    """
    Assert that :prop:`~adbts.timeouts.Timeout.exceeded` returns `True` after period
    has been exhausted.
    """
    with timeouts.Timeout(0.5) as timeout:
        assert not timeout.exceeded
        time.sleep(1)
        assert timeout.exceeded


def test_undefined_timeout_never_exceeded(undefined_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.exceeded` returns `False` when period is undefined.
    """
    with undefined_timeout as timeout:
        assert not timeout.exceeded
        time.sleep(1)
        assert not timeout.exceeded


def test_timeout_not_exceeded_when_elapsed_less_than_period():
    """
    Assert that :prop:`~adbts.timeouts.Timeout.exceeded` returns `False` when elapsed does not
    exceed the period.
    """
    with timeouts.Timeout(5) as timeout:
        assert not timeout.exceeded
        time.sleep(0.5)
        assert not timeout.exceeded


def test_elapsed_seconds_increments_when_not_stopped():
    """
    Assert that :prop:`~adbts.timeouts.Timeout.elapsed_seconds` continues to increment when
    it is not stopped.
    """
    with timeouts.Timeout(5) as timeout:
        for _ in range(0, 3):
            prev = timeout.elapsed_seconds
            time.sleep(1)
            assert timeout.elapsed_seconds >= prev + 1


def test_elapsed_seconds_stops_incrementing_when_stopped(stopped_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.elapsed_seconds` stops incrementing when stopped.
    """
    elapsed = stopped_timeout.elapsed_seconds
    time.sleep(1)
    assert stopped_timeout.elapsed_seconds == elapsed


def test_elapsed_millisseconds_increments_when_not_stopped():
    """
    Assert that :prop:`~adbts.timeouts.Timeout.elapsed_milliseconds` continues to increment when
    it is not stopped.
    """
    with timeouts.Timeout(5) as timeout:
        for _ in range(0, 3):
            prev = timeout.elapsed_milliseconds
            time.sleep(1)
            assert timeout.elapsed_milliseconds >= prev + 1000


def test_elapsed_milliseconds_stops_incrementing_when_stopped(stopped_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.elapsed_milliseconds` stops incrementing when stopped.
    """
    elapsed = stopped_timeout.elapsed_milliseconds
    time.sleep(1)
    assert stopped_timeout.elapsed_milliseconds == elapsed


def test_remaining_seconds_is_period_when_undefined(undefined_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.remaining_seconds` returns the period when
    it's an undefined timeout.
    """
    with undefined_timeout:
        assert undefined_timeout.remaining_seconds == undefined_timeout.period


def test_remaining_seconds_computes_delta():
    """
    Assert that :prop:`~adbts.timeouts.Timeout.remaining_seconds` computes its value from the
    elapsed time.
    """
    with timeouts.Timeout(5) as timeout:
        time.sleep(1)
        assert timeout.remaining_seconds == 4


def test_remaining_milliseconds_is_period_when_undefined(undefined_timeout):
    """
    Assert that :prop:`~adbts.timeouts.Timeout.remaining_milliseconds` returns the period when
    it's an undefined timeout.
    """
    with undefined_timeout:
        assert undefined_timeout.remaining_milliseconds == undefined_timeout.period


def test_remaining_milliseconds_computes_delta():
    """
    Assert that :prop:`~adbts.timeouts.Timeout.remaining_milliseconds` computes its value from the
    elapsed time.
    """
    with timeouts.Timeout(5) as timeout:
        time.sleep(1)
        assert timeout.remaining_milliseconds <= 4000


def test_wrap_returns_unmodified_when_given_timeout(not_started_timeout):
    """
    Assert that :meth:`~adbts.timeouts.wrap` returns the argument unmodified when given a
    :class:`~adbts.timeouts.Timeout` instance.
    """
    assert timeouts.wrap(not_started_timeout) is not_started_timeout


def test_wrap_converts_period_to_int(valid_period):
    """
    Assert that :meth:`~adbts.timeouts.wrap` converts the given numeric timeout value
    to a :class:`~int`.
    """
    timeout = timeouts.wrap(float(valid_period))
    assert timeout.period == valid_period


def test_wrap_supports_undefined_period():
    """
    Assert that :meth:`~adbts.timeouts.wrap` supports the undefined timeout sentinel value.
    """
    assert timeouts.wrap(timeouts.UNDEFINED).period is timeouts.UNDEFINED
