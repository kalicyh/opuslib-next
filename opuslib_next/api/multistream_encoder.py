#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
#

"""
CTypes mapping between libopus multistream encoder functions and Python.
"""

import array
import ctypes  # type: ignore
import functools
import typing

import opuslib_next
import opuslib_next.api

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


class MultiStreamEncoder(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """Opus multistream encoder state."""
    pass


MultiStreamEncoderPointer = ctypes.POINTER(MultiStreamEncoder)


def _require_function(name, argtypes, restype):
    try:
        func = getattr(opuslib_next.api.libopus, name)
    except AttributeError as exc:
        raise opuslib_next.OpusError(opuslib_next.UNIMPLEMENTED) from exc

    func.argtypes = argtypes
    func.restype = restype
    return func


@functools.lru_cache(maxsize=None)
def _libopus_get_size():
    return _require_function(
        'opus_multistream_encoder_get_size',
        (ctypes.c_int, ctypes.c_int),
        ctypes.c_int
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def get_size(streams: int, coupled_streams: int) -> typing.Union[int, typing.Any]:
    """Gets the size of an OpusMSEncoder structure."""
    return _libopus_get_size()(streams, coupled_streams)


@functools.lru_cache(maxsize=None)
def _libopus_create():
    return _require_function(
        'opus_multistream_encoder_create',
        (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            opuslib_next.api.c_ubyte_pointer,
            ctypes.c_int,
            opuslib_next.api.c_int_pointer
        ),
        MultiStreamEncoderPointer
    )


def create_state(
        fs: int,
        channels: int,
        streams: int,
        coupled_streams: int,
        mapping: typing.Sequence[int],
        application: int
) -> ctypes.Structure:
    """Allocates and initializes a multistream encoder state."""
    result_code = ctypes.c_int()
    mapping_array = (ctypes.c_ubyte * len(mapping))(*mapping)

    encoder_state = _libopus_create()(
        fs,
        channels,
        streams,
        coupled_streams,
        mapping_array,
        application,
        ctypes.byref(result_code)
    )

    if result_code.value != opuslib_next.OK:
        raise opuslib_next.OpusError(result_code.value)

    return encoder_state


@functools.lru_cache(maxsize=None)
def _libopus_encode():
    return _require_function(
        'opus_multistream_encode',
        (
            MultiStreamEncoderPointer,
            opuslib_next.api.c_int16_pointer,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int32
        ),
        ctypes.c_int32
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def encode(
        encoder_state: ctypes.Structure,
        pcm_data: bytes,
        frame_size: int,
        max_data_bytes: int
) -> typing.Union[bytes, typing.Any]:
    """Encodes an Opus frame from signed 16-bit PCM input."""
    pcm_pointer = ctypes.cast(pcm_data, opuslib_next.api.c_int16_pointer)
    opus_data = (ctypes.c_char * max_data_bytes)()

    result = _libopus_encode()(
        encoder_state,
        pcm_pointer,
        frame_size,
        opus_data,
        max_data_bytes
    )

    if result < 0:
        raise opuslib_next.OpusError(result)

    return array.array('b', opus_data[:result]).tobytes()


@functools.lru_cache(maxsize=None)
def _libopus_encode_float():
    return _require_function(
        'opus_multistream_encode_float',
        (
            MultiStreamEncoderPointer,
            opuslib_next.api.c_float_pointer,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int32
        ),
        ctypes.c_int32
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def encode_float(
        encoder_state: ctypes.Structure,
        pcm_data: bytes,
        frame_size: int,
        max_data_bytes: int
) -> typing.Union[bytes, typing.Any]:
    """Encodes an Opus frame from floating point input."""
    pcm_pointer = ctypes.cast(pcm_data, opuslib_next.api.c_float_pointer)
    opus_data = (ctypes.c_char * max_data_bytes)()

    result = _libopus_encode_float()(
        encoder_state,
        pcm_pointer,
        frame_size,
        opus_data,
        max_data_bytes
    )

    if result < 0:
        raise opuslib_next.OpusError(result)

    return array.array('b', opus_data[:result]).tobytes()


@functools.lru_cache(maxsize=None)
def _libopus_ctl():
    return _require_function(
        'opus_multistream_encoder_ctl',
        (MultiStreamEncoderPointer, ctypes.c_int),
        ctypes.c_int
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def encoder_ctl(
        encoder_state: ctypes.Structure,
        request,
        value=None
) -> typing.Union[int, typing.Any]:
    if value is not None:
        return request(_libopus_ctl(), encoder_state, value)
    return request(_libopus_ctl(), encoder_state)


@functools.lru_cache(maxsize=None)
def _libopus_destroy():
    return _require_function(
        'opus_multistream_encoder_destroy',
        (MultiStreamEncoderPointer,),
        None
    )


def destroy(encoder_state: ctypes.Structure) -> None:
    """Frees a multistream encoder allocated by create_state()."""
    _libopus_destroy()(encoder_state)
