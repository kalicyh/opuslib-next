#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import ctypes  # type: ignore
import unittest

import opuslib_next
import opuslib_next.api.ctl
import opuslib_next.api.multistream_decoder
import opuslib_next.api.multistream_encoder


class MultiStreamApiTest(unittest.TestCase):

    def setUp(self):
        try:
            opuslib_next.api.multistream_encoder.get_size(1, 1)
            opuslib_next.api.multistream_decoder.get_size(1, 1)
        except opuslib_next.OpusError as exc:
            if exc.code == opuslib_next.UNIMPLEMENTED:
                self.skipTest('libopus does not expose multistream APIs')
            raise

    def test_get_size(self):
        encoder_size = opuslib_next.api.multistream_encoder.get_size(1, 1)
        decoder_size = opuslib_next.api.multistream_decoder.get_size(1, 1)

        self.assertGreater(encoder_size, 0)
        self.assertGreater(decoder_size, 0)

        with self.assertRaises(TypeError):
            opuslib_next.api.multistream_encoder.get_size(1)

        with self.assertRaises(TypeError):
            opuslib_next.api.multistream_decoder.get_size(1)

    def test_create(self):
        enc = opuslib_next.api.multistream_encoder.create_state(
            48000, 2, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        dec = opuslib_next.api.multistream_decoder.create_state(
            48000, 2, 1, 1, [0, 1])

        opuslib_next.api.multistream_encoder.destroy(enc)
        opuslib_next.api.multistream_decoder.destroy(dec)

    def test_create_rejects_bad_args(self):
        with self.assertRaises(opuslib_next.OpusError) as enc_ctx:
            opuslib_next.api.multistream_encoder.create_state(
                1000, 2, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)

        with self.assertRaises(opuslib_next.OpusError) as dec_ctx:
            opuslib_next.api.multistream_decoder.create_state(
                1000, 2, 1, 1, [0, 1])

        self.assertEqual(enc_ctx.exception.code, opuslib_next.BAD_ARG)
        self.assertEqual(dec_ctx.exception.code, opuslib_next.BAD_ARG)

    def test_ctl_reset_state(self):
        enc = opuslib_next.api.multistream_encoder.create_state(
            48000, 2, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        dec = opuslib_next.api.multistream_decoder.create_state(
            48000, 2, 1, 1, [0, 1])

        opuslib_next.api.multistream_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.reset_state)
        opuslib_next.api.multistream_decoder.decoder_ctl(
            dec, opuslib_next.api.ctl.reset_state)

        opuslib_next.api.multistream_encoder.destroy(enc)
        opuslib_next.api.multistream_decoder.destroy(dec)

    def test_encode_decode_roundtrip(self):
        frame_size = 960
        channels = 2
        enc = opuslib_next.api.multistream_encoder.create_state(
            48000, channels, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        dec = opuslib_next.api.multistream_decoder.create_state(
            48000, channels, 1, 1, [0, 1])
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_int16) * channels * frame_size

        packet = opuslib_next.api.multistream_encoder.encode(
            enc, pcm, frame_size, 4000)
        decoded = opuslib_next.api.multistream_decoder.decode(
            dec, packet, len(packet), frame_size, False, channels=channels)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_int16) * channels * frame_size
        )

        opuslib_next.api.multistream_encoder.destroy(enc)
        opuslib_next.api.multistream_decoder.destroy(dec)

    def test_encode_decode_float_roundtrip(self):
        frame_size = 960
        channels = 2
        enc = opuslib_next.api.multistream_encoder.create_state(
            48000, channels, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        dec = opuslib_next.api.multistream_decoder.create_state(
            48000, channels, 1, 1, [0, 1])
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_float) * channels * frame_size

        packet = opuslib_next.api.multistream_encoder.encode_float(
            enc, pcm, frame_size, 4000)
        decoded = opuslib_next.api.multistream_decoder.decode_float(
            dec, packet, len(packet), frame_size, False, channels=channels)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_float) * channels * frame_size
        )

        opuslib_next.api.multistream_encoder.destroy(enc)
        opuslib_next.api.multistream_decoder.destroy(dec)
