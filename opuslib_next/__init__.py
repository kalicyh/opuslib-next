# OpusLib Python Module.

"""
OpusLib Python Module.
~~~~~~~

Python bindings to the libopus, IETF low-delay audio codec

:author: kalicyh <kalicyh@qq.com>
:copyright: Copyright (c) 2025, Kalicyh
:license: BSD 3-Clause License
:source: <https://github.com/kalicyh/opuslib-next>

"""

from .exceptions import OpusError

from .constants import *

from .classes import (
    Decoder,
    Encoder,
    MultiStreamDecoder,
    MultiStreamEncoder,
    ProjectionDecoder,
    ProjectionEncoder,
)
