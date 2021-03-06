"""
    adbtp.async
    ~~~~~~~~~~~

    Contains functionality for asynchronous transport protocols.
"""
import asyncio

import adbts
import adbwp

from . import exceptions, hints, protocol, timeouts

__all__ = ['Protocol']


class Protocol(protocol.Protocol):
    """
    Defines asynchronous (non-blocking) transport protocol.
    """

    def __init__(self, transport):
        self._transport = transport
        self._read_lock = None
        self._write_lock = None

    @property
    def closed(self):
        """
        Checks to see if the protocol is closed.

        :return: Closed state of the protocol
        :rtype: :class:`~bool`
        """
        return self._transport and self._transport.closed

    @asyncio.coroutine
    @protocol.ensure_opened
    def read(self, timeout: hints.Timeout=timeouts.UNDEFINED):
        """
        Read a message from the protocol.

        :param timeout: Maximum number of milliseconds to read before raising an exception
        :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
        :return: A message read from the protocol
        :rtype: :class:`~adbwp.message.Message`
        """
        with self._read_lock:
            with timeouts.wrap(timeout) as timeout:
                header = yield from read_header(self._transport, timeout)
                message = yield from read_payload(header, self._transport, timeout)
                return message

    @asyncio.coroutine
    @protocol.ensure_opened
    def write(self, message, timeout: hints.Timeout=timeouts.UNDEFINED):
        """
        Write a message to the protocol.

        :param message: Message to write
        :type message: :class:`~adbwp.message.Message`
        :param timeout: Maximum number of milliseconds to read before raising an exception
        :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        with self._write_lock:
            with timeouts.wrap(timeout) as timeout:
                yield from write_header(message.header, self._transport, timeout)
                yield from write_payload(message, self._transport, timeout)

    @protocol.ensure_opened
    def close(self):
        """
        Close the protocol.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        self._transport.close()
        self._transport = None


@asyncio.coroutine
@exceptions.reraise((adbts.TransportError, adbwp.WireProtocolError))
@exceptions.reraise_timeout_errors(adbts.TransportTimeoutError)
def read_header(transport, timeout):
    """
    Read bytes from the transport to create a new :class:`~adbwp.header.Header`.

    :param transport: Transport to read from
    :type transport: :class:`~adbts.transport.Transport`
    :param timeout: Maximum number of milliseconds to read before raising an exception
    :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
    :return: Message header read from transport
    :rtype: :class:`~adbwp.header.Header`
    :raises :class:`~adbtp.exceptions.TransportProtocolError` When transport or wire-protocol raise exceptions
    :raises :class:`~adbtp.exceptions.TransportProtocolTimeoutError` When transport action exceeds timeout
    """
    header_bytes = yield from transport.read(adbwp.header.BYTES, timeout=timeout.remaining_milliseconds)
    return adbwp.header.from_bytes(header_bytes)


@asyncio.coroutine
@exceptions.reraise((adbts.TransportError, adbwp.WireProtocolError))
@exceptions.reraise_timeout_errors(adbts.TransportTimeoutError)
def read_payload(header, transport, timeout):
    """
    Read optional 'data_length' number of bytes from the transport
    to create a new :class:`~adbwp.message.Message`.

    :param header: Header to read data payload for
    :type header: :class:`~adbwp.header.Header`
    :param transport: Transport to read from
    :type transport: :class:`~adbts.transport.Transport`
    :param timeout: Maximum number of milliseconds to read before raising an exception
    :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
    :return: Message from header and payload bytes read from transport
    :rtype: :class:`~adbwp.message.Message`
    :raises :class:`~adbtp.exceptions.TransportProtocolError` When transport or wire-protocol raise exceptions
    :raises :class:`~adbtp.exceptions.TransportProtocolTimeoutError` When transport action exceeds timeout
    """
    data_bytes = yield from transport.read(header.data_length,
                                           timeout=timeout.remaining_milliseconds or timeouts.OVERAGE)
    return adbwp.message.from_header(header, data_bytes)


@asyncio.coroutine
@exceptions.reraise((adbts.TransportError, adbwp.WireProtocolError))
@exceptions.reraise_timeout_errors(adbts.TransportTimeoutError)
def write_header(header, transport, timeout):
    """
    Write given :class:`~adbwp.header.Header` header as bytes to the transport.

    :param header: Header to serialize and write to transport
    :type header: :class:`~adbwp.header.Header`
    :param transport: Transport to write to
    :type transport: :class:`~adbts.transport.Transport`
    :param timeout: Maximum number of milliseconds to write before raising an exception
    :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
    :return: Nothing
    :rtype: :class:`~NoneType`
    :raises :class:`~adbtp.exceptions.TransportProtocolError` When transport or wire-protocol raise exceptions
    :raises :class:`~adbtp.exceptions.TransportProtocolTimeoutError` When transport action exceeds timeout
    """
    yield from transport.write(adbwp.header.to_bytes(header), timeout=timeout.remaining_milliseconds)


@asyncio.coroutine
@exceptions.reraise((adbts.TransportError, adbwp.WireProtocolError))
@exceptions.reraise_timeout_errors(adbts.TransportTimeoutError)
def write_payload(message, transport, timeout):
    """
    Write given :class:`~adbwp.message.Message` data payload to the transport.

    :param message: Message with data payload to write to transport
    :type message: :class:`~adbwp.message.Message`
    :param transport: Transport to write to
    :type transport: :class:`~adbts.transport.Transport`
    :param timeout: Maximum number of milliseconds to write before raising an exception
    :type timeout: :class:`~int`, :class:`~NoneType`, or :class:`~object`
    :return: Nothing
    :rtype: :class:`~NoneType`
    :raises :class:`~adbtp.exceptions.TransportProtocolError` When transport or wire-protocol raise exceptions
    :raises :class:`~adbtp.exceptions.TransportProtocolTimeoutError` When transport action exceeds timeout
    """
    yield from transport.write(message.data, timeout=timeout.remaining_milliseconds or timeouts.OVERAGE)
