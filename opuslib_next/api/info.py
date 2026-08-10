import ctypes

import opuslib_next.api


strerror = opuslib_next.api.libopus.opus_strerror
strerror.argtypes = (ctypes.c_int,)  # must be sequence (,) of types!
strerror.restype = ctypes.c_char_p
strerror.__doc__ = 'Converts an opus error code into a human readable string'


get_version_string = opuslib_next.api.libopus.opus_get_version_string
get_version_string.argtypes = None
get_version_string.restype = ctypes.c_char_p
get_version_string.__doc__ = 'Gets the libopus version string'
