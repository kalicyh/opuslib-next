#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,too-few-public-methods
#

"""
CTypes mapping between libopus multistream decoder functions and Python.
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


class MultiStreamDecoder(ctypes.Structure):
    """Opus multistream decoder state."""
    pass


MultiStreamDecoderPointer = ctypes.POINTER(MultiStreamDecoder)


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
        'opus_multistream_decoder_get_size',
        (ctypes.c_int, ctypes.c_int),
        ctypes.c_int
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def get_size(streams: int, coupled_streams: int) -> typing.Union[int, typing.Any]:
    """Gets the size of an OpusMSDecoder structure."""
    return _libopus_get_size()(streams, coupled_streams)


@functools.lru_cache(maxsize=None)
def _libopus_create():
    return _require_function(
        'opus_multistream_decoder_create',
        (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            opuslib_next.api.c_ubyte_pointer,
            opuslib_next.api.c_int_pointer
        ),
        MultiStreamDecoderPointer
    )


def create_state(
        fs: int,
        channels: int,
        streams: int,
        coupled_streams: int,
        mapping: typing.Sequence[int]
) -> ctypes.Structure:
    """Allocates and initializes a multistream decoder state."""
    result_code = ctypes.c_int()
    mapping_array = (ctypes.c_ubyte * len(mapping))(*mapping)

    decoder_state = _libopus_create()(
        fs,
        channels,
        streams,
        coupled_streams,
        mapping_array,
        ctypes.byref(result_code)
    )

    if result_code.value != opuslib_next.OK:
        raise opuslib_next.exceptions.OpusError(result_code.value)

    return decoder_state


@functools.lru_cache(maxsize=None)
def _libopus_decode():
    return _require_function(
        'opus_multistream_decode',
        (
            MultiStreamDecoderPointer,
            ctypes.c_char_p,
            ctypes.c_int32,
            opuslib_next.api.c_int16_pointer,
            ctypes.c_int,
            ctypes.c_int
        ),
        ctypes.c_int
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def decode(  # pylint: disable=too-many-arguments
        decoder_state: ctypes.Structure,
        opus_data: bytes,
        length: int,
        frame_size: int,
        decode_fec: bool,
        channels: int = 2
) -> typing.Union[bytes, typing.Any]:
    """Decodes an Opus packet to signed 16-bit PCM."""
    pcm_size = frame_size * channels
    pcm = (ctypes.c_int16 * pcm_size)()
    pcm_pointer = ctypes.cast(pcm, opuslib_next.api.c_int16_pointer)

    result = _libopus_decode()(
        decoder_state,
        opus_data,
        length,
        pcm_pointer,
        frame_size,
        int(decode_fec)
    )

    if result < 0:
        raise opuslib_next.exceptions.OpusError(result)

    return array.array('h', pcm_pointer[:result * channels]).tobytes()


@functools.lru_cache(maxsize=None)
def _libopus_decode_float():
    return _require_function(
        'opus_multistream_decode_float',
        (
            MultiStreamDecoderPointer,
            ctypes.c_char_p,
            ctypes.c_int32,
            opuslib_next.api.c_float_pointer,
            ctypes.c_int,
            ctypes.c_int
        ),
        ctypes.c_int
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def decode_float(  # pylint: disable=too-many-arguments
        decoder_state: ctypes.Structure,
        opus_data: bytes,
        length: int,
        frame_size: int,
        decode_fec: bool,
        channels: int = 2
) -> typing.Union[bytes, typing.Any]:
    """Decodes an Opus packet to floating point PCM."""
    pcm_size = frame_size * channels
    pcm = (ctypes.c_float * pcm_size)()
    pcm_pointer = ctypes.cast(pcm, opuslib_next.api.c_float_pointer)

    result = _libopus_decode_float()(
        decoder_state,
        opus_data,
        length,
        pcm_pointer,
        frame_size,
        int(decode_fec)
    )

    if result < 0:
        raise opuslib_next.exceptions.OpusError(result)

    return array.array('f', pcm[:result * channels]).tobytes()


@functools.lru_cache(maxsize=None)
def _libopus_ctl():
    return _require_function(
        'opus_multistream_decoder_ctl',
        (MultiStreamDecoderPointer, ctypes.c_int),
        ctypes.c_int
    )


# FIXME: Remove typing.Any once we have a stub for ctypes
def decoder_ctl(
        decoder_state: ctypes.Structure,
        request,
        value=None
) -> typing.Union[int, typing.Any]:
    if value is not None:
        return request(_libopus_ctl(), decoder_state, value)
    return request(_libopus_ctl(), decoder_state)


@functools.lru_cache(maxsize=None)
def _libopus_destroy():
    return _require_function(
        'opus_multistream_decoder_destroy',
        (MultiStreamDecoderPointer,),
        None
    )


def destroy(decoder_state: ctypes.Structure) -> None:
    """Frees a multistream decoder allocated by create_state()."""
    _libopus_destroy()(decoder_state)
