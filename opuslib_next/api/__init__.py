#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
#

"""OpusLib Package."""

import ctypes  # type: ignore
import os
import platform
from ctypes.util import find_library  # type: ignore

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


lib_location = find_library('opus')

if lib_location is None:
    # find opus library in macOS
    if platform.system() == 'Darwin':
        lib_paths = [
            '/opt/homebrew/lib/libopus.dylib',
            '/usr/local/lib/libopus.dylib',
        ]
        
        for path in lib_paths:
            if os.path.exists(path):
                lib_location = path
                break
    
if lib_location is None:
    raise Exception(
        'Could not find Opus library. Make sure it is installed.')

libopus = ctypes.CDLL(lib_location)

c_int_pointer = ctypes.POINTER(ctypes.c_int)
c_int16_pointer = ctypes.POINTER(ctypes.c_int16)
c_float_pointer = ctypes.POINTER(ctypes.c_float)
