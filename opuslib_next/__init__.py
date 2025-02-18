#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from .exceptions import OpusError  # NOQA

from .constants import *  # NOQA

from .constants import OK, APPLICATION_TYPES_MAP  # NOQA

from .classes import Encoder, Decoder  # NOQA

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'
