"""
    adbtp.hints
    ~~~~~~~~~~~

    Contains type hint definitions used across modules in this package.
"""
import typing

import adbts

# pylint: disable=invalid-name,no-member,unsubscriptable-object

#: Type hint that is an alias for the built-in :class:`~bool` type.
Bool = bool


#: Type hint that is an alias for the built-in :class:`~float` type.
Float = float


#: Type hint that is an alias for the built-in :class:`~int` type.
Int = int


#: Type hint that is an alias for the built-in :class:`~str` type.
Str = str


#: Type hint that defines an optional integer value that represents
#: a timeout value to a transport.
Timeout = typing.Optional[typing.Union[int, float]]


#: Type hint that represents an ADB transport.
Transport = adbts.Transport
