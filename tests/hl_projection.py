#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import ctypes  # type: ignore
import unittest

import opuslib_next
import opuslib_next.api.projection_decoder
import opuslib_next.api.projection_encoder


CHANNELS = 4
MAPPING_FAMILY = 3


class HighLevelProjectionTest(unittest.TestCase):

    def setUp(self):
        try:
            opuslib_next.api.projection_encoder.get_size(
                CHANNELS, MAPPING_FAMILY)
            opuslib_next.api.projection_decoder.get_size(CHANNELS, 2, 2)
        except opuslib_next.OpusError as exc:
            if exc.code == opuslib_next.UNIMPLEMENTED:
                self.skipTest('libopus does not expose projection APIs')
            raise

    def _create_encoder(self):
        return opuslib_next.ProjectionEncoder(
            48000, CHANNELS, MAPPING_FAMILY, 'audio')

    def _create_encoder_and_decoder(self):
        encoder = self._create_encoder()
        decoder = opuslib_next.ProjectionDecoder(
            48000,
            CHANNELS,
            encoder.streams,
            encoder.coupled_streams,
            encoder.demixing_matrix
        )

        return encoder, decoder

    def test_create(self):
        encoder, decoder = self._create_encoder_and_decoder()

        self.assertEqual(encoder.streams, 2)
        self.assertEqual(encoder.coupled_streams, 2)
        self.assertEqual(decoder.streams, encoder.streams)
        self.assertEqual(decoder.coupled_streams, encoder.coupled_streams)

    def test_demixing_matrix_properties(self):
        encoder = self._create_encoder()

        self.assertIsInstance(encoder.demixing_matrix_gain, int)
        self.assertGreater(encoder.demixing_matrix_size, 0)
        self.assertEqual(
            len(encoder.demixing_matrix),
            encoder.demixing_matrix_size
        )
        self.assertEqual(
            len(encoder.get_demixing_matrix()),
            encoder.demixing_matrix_size
        )

    def test_reset_state(self):
        encoder, decoder = self._create_encoder_and_decoder()

        encoder.reset_state()
        decoder.reset_state()

    def test_encode_decode_roundtrip(self):
        frame_size = 960
        encoder, decoder = self._create_encoder_and_decoder()
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_int16) * CHANNELS * frame_size

        packet = encoder.encode(pcm, frame_size)
        decoded = decoder.decode(packet, frame_size)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_int16) * CHANNELS * frame_size
        )

    def test_encode_decode_float_roundtrip(self):
        frame_size = 960
        encoder, decoder = self._create_encoder_and_decoder()
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_float) * CHANNELS * frame_size

        packet = encoder.encode_float(pcm, frame_size)
        decoded = decoder.decode_float(packet, frame_size)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_float) * CHANNELS * frame_size
        )

    def test_encoder_properties(self):
        encoder = self._create_encoder()

        encoder.complexity = 5
        self.assertEqual(encoder.complexity, 5)

        encoder.bitrate = 48000
        self.assertGreater(encoder.bitrate, 0)

        encoder.inband_fec = 1
        self.assertEqual(encoder.inband_fec, 1)

        encoder.packet_loss_perc = 10
        self.assertEqual(encoder.packet_loss_perc, 10)

    def test_decoder_gain_property(self):
        _, decoder = self._create_encoder_and_decoder()

        decoder.gain = -15
        self.assertEqual(decoder.gain, -15)
