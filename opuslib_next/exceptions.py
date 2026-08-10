"""
Exceptions for OpusLib.
"""

import typing

import opuslib_next.api.info


class OpusError(Exception):

    """
    Generic handler for OpusLib errors from C library.
    """

    def __init__(self, code: int) -> None:
        self.code = code
        super().__init__()

    # FIXME: Remove typing.Any once we have a stub for ctypes
    def __str__(self) -> typing.Union[str, typing.Any]:
        message = opuslib_next.api.info.strerror(self.code)
        if isinstance(message, bytes):
            return message.decode("utf-8", errors="replace")
        return str(message)
