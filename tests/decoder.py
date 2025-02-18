#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import sys
import unittest

import opuslib.api
import opuslib.api.decoder
import opuslib.api.ctl

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


class DecoderTest(unittest.TestCase):
    """Decoder basic API tests

    From the `tests/test_opus_api.c`
    """

    def test_get_size(self):
        """Invalid configurations which should fail"""

        for csx in range(4):
            ixx = opuslib.api.decoder.libopus_get_size(csx)
            if csx in (1, 2):
                self.assertFalse(1 << 16 < ixx <= 2048)
            else:
                self.assertEqual(ixx, 0)

    def _test_unsupported_sample_rates(self):
        """
        Unsupported sample rates

        TODO: make the same test with a opus_decoder_init() function
        """
        for csx in range(4):
            for ixx in range(-7, 96000):
                if ixx in (8000, 12000, 16000, 24000, 48000) and csx in (1, 2):
                    continue

                if ixx == -5:
                    fsx = -8000
                elif ixx == -6:
                    fsx = sys.maxsize  # TODO: should be a INT32_MAX
                elif ixx == -7:
                    fsx = -1 * (sys.maxsize - 1)  # Emulation of the INT32_MIN
                else:
                    fsx = ixx

                try:
                    dec = opuslib.api.decoder.create_state(fsx, csx)
                except opuslib.OpusError as exc:
                    self.assertEqual(exc.code, opuslib.BAD_ARG)
                else:
                    opuslib.api.decoder.destroy(dec)

    @classmethod
    def test_create(cls):
        try:
            dec = opuslib.api.decoder.create_state(48000, 2)
        except opuslib.OpusError:
            raise AssertionError()
        else:
            opuslib.api.decoder.destroy(dec)

            # TODO: rewrite this code
        # VG_CHECK(dec,opus_decoder_get_size(2));

    @classmethod
    def test_get_final_range(cls):
        dec = opuslib.api.decoder.create_state(48000, 2)
        opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.get_final_range)
        opuslib.api.decoder.destroy(dec)

    def test_unimplemented(self):
        dec = opuslib.api.decoder.create_state(48000, 2)

        try:
            opuslib.api.decoder.decoder_ctl(
                dec, opuslib.api.ctl.unimplemented)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.UNIMPLEMENTED)

        opuslib.api.decoder.destroy(dec)

    def test_get_bandwidth(self):
        dec = opuslib.api.decoder.create_state(48000, 2)
        value = opuslib.api.decoder.decoder_ctl(
            dec, opuslib.api.ctl.get_bandwidth)
        self.assertEqual(value, 0)
        opuslib.api.decoder.destroy(dec)

    def test_get_pitch(self):
        dec = opuslib.api.decoder.create_state(48000, 2)

        i = opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.get_pitch)
        self.assertIn(i, (-1, 0))

        packet = bytes([252, 0, 0])
        opuslib.api.decoder.decode(dec, packet, 3, 960, False)
        i = opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.get_pitch)
        self.assertIn(i, (-1, 0))

        packet = bytes([1, 0, 0])
        opuslib.api.decoder.decode(dec, packet, 3, 960, False)
        i = opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.get_pitch)
        self.assertIn(i, (-1, 0))

        opuslib.api.decoder.destroy(dec)

    def test_gain(self):
        dec = opuslib.api.decoder.create_state(48000, 2)

        i = opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.get_gain)
        self.assertEqual(i, 0)

        try:
            opuslib.api.decoder.decoder_ctl(
                dec, opuslib.api.ctl.set_gain, -32769)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BAD_ARG)

        try:
            opuslib.api.decoder.decoder_ctl(
                dec, opuslib.api.ctl.set_gain, 32768)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BAD_ARG)

        opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.set_gain, -15)
        i = opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.get_gain)
        self.assertEqual(i, -15)

        opuslib.api.decoder.destroy(dec)

    @classmethod
    def test_reset_state(cls):
        dec = opuslib.api.decoder.create_state(48000, 2)
        opuslib.api.decoder.decoder_ctl(dec, opuslib.api.ctl.reset_state)
        opuslib.api.decoder.destroy(dec)

    def test_get_nb_samples(self):
        """opus_decoder_get_nb_samples()"""

        dec = opuslib.api.decoder.create_state(48000, 2)

        self.assertEqual(
            480, opuslib.api.decoder.get_nb_samples(dec, bytes([0]), 1))

        packet = bytes()
        for xxc in ((63 << 2) | 3, 63):
            packet += bytes([xxc])

        # TODO: check for exception code
        self.assertRaises(
            opuslib.OpusError,
            lambda: opuslib.api.decoder.get_nb_samples(dec, packet, 2)
        )

        opuslib.api.decoder.destroy(dec)

    def test_packet_get_nb_frames(self):
        """opus_packet_get_nb_frames()"""

        packet = bytes()
        for xxc in ((63 << 2) | 3, 63):
            packet += bytes([xxc])

        self.assertRaises(
            opuslib.OpusError,
            lambda: opuslib.api.decoder.packet_get_nb_frames(packet, 0)
        )

        l1res = (1, 2, 2, opuslib.INVALID_PACKET)

        for ixc in range(0, 256):
            packet = bytes([ixc])
            expected_result = l1res[ixc & 3]

            try:
                self.assertEqual(
                    expected_result,
                    opuslib.api.decoder.packet_get_nb_frames(packet, 1)
                )
            except opuslib.OpusError as exc:
                if exc.code == expected_result:
                    continue

            for jxc in range(0, 256):
                packet = bytes([ixc, jxc])

                self.assertEqual(
                    expected_result if expected_result != 3 else (packet[1] & 63),  # NOQA
                    opuslib.api.decoder.packet_get_nb_frames(packet, 2)
                )

    def test_packet_get_bandwidth(self):
        """Tests `opuslib.api.decoder.opus_packet_get_bandwidth()`"""

        for ixc in range(0, 256):
            packet = bytes([ixc])
            bwx = ixc >> 4

            # Very cozy code from the test_opus_api.c
            _bwx = opuslib.BANDWIDTH_NARROWBAND + (((((bwx & 7) * 9) & (63 - (bwx & 8))) + 2 + 12 * ((bwx & 8) != 0)) >> 4)  # NOQA pylint: disable=line-too-long

            self.assertEqual(
                _bwx, opuslib.api.decoder.packet_get_bandwidth(packet)
            )

    def test_decode(self):
        """opus_decode()"""

        packet = bytes([255, 49])
        for _ in range(2, 51):
            packet += bytes([0])

        dec = opuslib.api.decoder.create_state(48000, 2)
        try:
            opuslib.api.decoder.decode(dec, packet, 51, 960, 0)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.INVALID_PACKET)

        packet = bytes([252, 0, 0])
        try:
            opuslib.api.decoder.decode(dec, packet, -1, 960, 0)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BAD_ARG)

        try:
            opuslib.api.decoder.decode(dec, packet, 3, 60, 0)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BUFFER_TOO_SMALL)

        try:
            opuslib.api.decoder.decode(dec, packet, 3, 480, 0)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BUFFER_TOO_SMALL)

        try:
            opuslib.api.decoder.decode(dec, packet, 3, 960, 0)
        except opuslib.OpusError:
            self.fail('Decode failed')

        opuslib.api.decoder.destroy(dec)

    def test_decode_float(self):
        dec = opuslib.api.decoder.create_state(48000, 2)

        packet = bytes([252, 0, 0])

        try:
            opuslib.api.decoder.decode_float(dec, packet, 3, 960, 0)
        except opuslib.OpusError:
            self.fail('Decode failed')

        opuslib.api.decoder.destroy(dec)
