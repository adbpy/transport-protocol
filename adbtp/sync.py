"""
    adbtp.sync
    ~~~~~~~~~~

    Contains functionality for synchronous transport protocols.
"""
import threading

import adbts
import adbwp

from . import exceptions, hints, protocol, timeouts

__all__ = ['Protocol', 'open']


class Protocol(protocol.Protocol):
    """
    Defines synchronous (blocking) transport protocol.
    """

    def __init__(self, transport):
        super().__init__(transport)
        self._read_lock = threading.RLock()
        self._write_lock = threading.RLock()
        self._close_lock = threading.RLock()

    @property
    def closed(self):
        """
        Checks to see if the protocol is closed.

        :return: Closed state of the protocol
        :rtype: :class:`~bool`
        """
        return not self._transport or self._transport.closed

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
                header = read_header(self._transport, timeout)
                return read_payload(header, self._transport, timeout)

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
                write_header(message.header, self._transport, timeout)
                write_payload(message, self._transport, timeout)

    @protocol.ensure_opened
    def close(self):
        """
        Close the protocol.

        :return: Nothing
        :rtype: :class:`~NoneType`
        """
        with self._close_lock:
            self._transport.close()
            self._transport = None


@exceptions.reraise((adbts.TransportError, adbwp.WireProtocolError))
@exceptions.reraise_timeout_errors(adbts.TransportTimeoutError)
def open(transport):  # pylint: disable=redefined-builtin
    """
    Open a new :class:`~adbtp.sync.Protocol` using the given synchronous transport.

    :param transport: Synchronous transport to use with the protocol
    :rtype transport: :class:`~adbts.transport.Transport`
    :return: A synchronous protocol
    :rtype: :class:`~adbtp.sync.Protocol`
    """
    return Protocol(transport)


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
    header_bytes = transport.read(adbwp.header.BYTES, timeout=timeout.remaining_milliseconds)
    return adbwp.header.from_bytes(header_bytes)


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
    data_bytes = transport.read(header.data_length, timeout=timeout.remaining_milliseconds or timeouts.OVERAGE)
    return adbwp.message.from_header(header, data_bytes)


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
    transport.write(adbwp.header.to_bytes(header), timeout=timeout.remaining_milliseconds)


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
    transport.write(message.data, timeout=timeout.remaining_milliseconds or timeouts.OVERAGE)
