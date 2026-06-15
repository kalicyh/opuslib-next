#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import ctypes  # type: ignore
import unittest

import opuslib_next
import opuslib_next.api.ctl
import opuslib_next.api.projection_decoder
import opuslib_next.api.projection_encoder


CHANNELS = 4
MAPPING_FAMILY = 3


class ProjectionApiTest(unittest.TestCase):

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
        return opuslib_next.api.projection_encoder.create_state(
            48000,
            CHANNELS,
            MAPPING_FAMILY,
            opuslib_next.APPLICATION_AUDIO
        )

    def _create_decoder(self, streams, coupled_streams, demixing_matrix):
        return opuslib_next.api.projection_decoder.create_state(
            48000,
            CHANNELS,
            streams,
            coupled_streams,
            demixing_matrix
        )

    def _create_encoder_and_decoder(self):
        enc, streams, coupled_streams = self._create_encoder()
        matrix_size = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix_size)
        demixing_matrix = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix, matrix_size)
        dec = self._create_decoder(streams, coupled_streams, demixing_matrix)

        return enc, dec, streams, coupled_streams, demixing_matrix

    def test_get_size(self):
        encoder_size = opuslib_next.api.projection_encoder.get_size(
            CHANNELS, MAPPING_FAMILY)
        decoder_size = opuslib_next.api.projection_decoder.get_size(
            CHANNELS, 2, 2)

        self.assertGreater(encoder_size, 0)
        self.assertGreater(decoder_size, 0)

        with self.assertRaises(TypeError):
            opuslib_next.api.projection_encoder.get_size(CHANNELS)

        with self.assertRaises(TypeError):
            opuslib_next.api.projection_decoder.get_size(CHANNELS, 2)

    def test_create_and_demixing_matrix(self):
        enc, streams, coupled_streams = self._create_encoder()

        self.assertEqual(streams, 2)
        self.assertEqual(coupled_streams, 2)

        matrix_gain = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix_gain)
        matrix_size = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix_size)
        demixing_matrix = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix, matrix_size)
        dec = self._create_decoder(streams, coupled_streams, demixing_matrix)

        self.assertIsInstance(matrix_gain, int)
        self.assertGreater(matrix_size, 0)
        self.assertEqual(len(demixing_matrix), matrix_size)

        opuslib_next.api.projection_encoder.destroy(enc)
        opuslib_next.api.projection_decoder.destroy(dec)

    def test_create_rejects_bad_args(self):
        enc, streams, coupled_streams = self._create_encoder()
        matrix_size = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix_size)
        demixing_matrix = opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_demixing_matrix, matrix_size)

        with self.assertRaises(opuslib_next.OpusError) as enc_ctx:
            opuslib_next.api.projection_encoder.create_state(
                1000,
                CHANNELS,
                MAPPING_FAMILY,
                opuslib_next.APPLICATION_AUDIO
            )

        with self.assertRaises(opuslib_next.OpusError) as dec_ctx:
            opuslib_next.api.projection_decoder.create_state(
                1000,
                CHANNELS,
                streams,
                coupled_streams,
                demixing_matrix
            )

        self.assertEqual(enc_ctx.exception.code, opuslib_next.BAD_ARG)
        self.assertEqual(dec_ctx.exception.code, opuslib_next.BAD_ARG)

        opuslib_next.api.projection_encoder.destroy(enc)

    def test_ctl_reset_state(self):
        enc, dec, _, _, _ = self._create_encoder_and_decoder()

        opuslib_next.api.projection_encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.reset_state)
        opuslib_next.api.projection_decoder.decoder_ctl(
            dec, opuslib_next.api.ctl.reset_state)

        opuslib_next.api.projection_encoder.destroy(enc)
        opuslib_next.api.projection_decoder.destroy(dec)

    def test_encode_decode_roundtrip(self):
        frame_size = 960
        enc, dec, _, _, _ = self._create_encoder_and_decoder()
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_int16) * CHANNELS * frame_size

        packet = opuslib_next.api.projection_encoder.encode(
            enc, pcm, frame_size, 4000)
        decoded = opuslib_next.api.projection_decoder.decode(
            dec, packet, len(packet), frame_size, False, channels=CHANNELS)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_int16) * CHANNELS * frame_size
        )

        opuslib_next.api.projection_encoder.destroy(enc)
        opuslib_next.api.projection_decoder.destroy(dec)

    def test_encode_decode_float_roundtrip(self):
        frame_size = 960
        enc, dec, _, _, _ = self._create_encoder_and_decoder()
        pcm = b'\x00' * ctypes.sizeof(ctypes.c_float) * CHANNELS * frame_size

        packet = opuslib_next.api.projection_encoder.encode_float(
            enc, pcm, frame_size, 4000)
        decoded = opuslib_next.api.projection_decoder.decode_float(
            dec, packet, len(packet), frame_size, False, channels=CHANNELS)

        self.assertGreater(len(packet), 0)
        self.assertEqual(
            len(decoded),
            ctypes.sizeof(ctypes.c_float) * CHANNELS * frame_size
        )

        opuslib_next.api.projection_encoder.destroy(enc)
        opuslib_next.api.projection_decoder.destroy(dec)
