#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import ctypes  # type: ignore
import unittest

import opuslib_next
import opuslib_next.api.multistream_decoder
import opuslib_next.api.multistream_encoder


class HighLevelMultiStreamTest(unittest.TestCase):

    def setUp(self):
        try:
            opuslib_next.api.multistream_encoder.get_size(1, 1)
            opuslib_next.api.multistream_decoder.get_size(1, 1)
        except opuslib_next.OpusError as exc:
            if exc.code == opuslib_next.UNIMPLEMENTED:
                self.skipTest('libopus does not expose multistream APIs')
            raise

    def test_create(self):
        opuslib_next.MultiStreamEncoder(
            48000, 2, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        opuslib_next.MultiStreamDecoder(48000, 2, 1, 1, [0, 1])

    def test_reset_state(self):
        encoder = opuslib_next.MultiStreamEncoder(
            48000, 2, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        decoder = opuslib_next.MultiStreamDecoder(48000, 2, 1, 1, [0, 1])

        encoder.reset_state()
        decoder.reset_state()

    def test_encode_decode_roundtrip(self):
        frame_size = 960
        channels = 2
        encoder = opuslib_next.MultiStreamEncoder(
            48000, channels, 1, 1, [0, 1], 'audio')
        decoder = opuslib_next.MultiStreamDecoder(
            48000, channels, 1, 1, [0, 1])
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_int16) * channels * frame_size

        packet = encoder.encode(pcm, frame_size)
        decoded = decoder.decode(packet, frame_size)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_int16) * channels * frame_size
        )

    def test_encode_decode_float_roundtrip(self):
        frame_size = 960
        channels = 2
        encoder = opuslib_next.MultiStreamEncoder(
            48000, channels, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)
        decoder = opuslib_next.MultiStreamDecoder(
            48000, channels, 1, 1, [0, 1])
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_float) * channels * frame_size

        packet = encoder.encode_float(pcm, frame_size)
        decoded = decoder.decode_float(packet, frame_size)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_float) * channels * frame_size
        )

    def test_encoder_properties(self):
        encoder = opuslib_next.MultiStreamEncoder(
            48000, 2, 1, 1, [0, 1], opuslib_next.APPLICATION_AUDIO)

        encoder.complexity = 5
        self.assertEqual(encoder.complexity, 5)

        encoder.bitrate = 24000
        self.assertGreater(encoder.bitrate, 0)

        encoder.inband_fec = 1
        self.assertEqual(encoder.inband_fec, 1)

        encoder.packet_loss_perc = 10
        self.assertEqual(encoder.packet_loss_perc, 10)

    def test_decoder_gain_property(self):
        decoder = opuslib_next.MultiStreamDecoder(48000, 2, 1, 1, [0, 1])

        decoder.gain = -15
        self.assertEqual(decoder.gain, -15)
