#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import ctypes  # type: ignore
import sys
import unittest

import opuslib_next.api
import opuslib_next.api.encoder
import opuslib_next.api.ctl

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


class EncoderTest(unittest.TestCase):
    """Encoder basic API tests

    From the `tests/test_opus_api.c`
    """

    def _test_unsupported_sample_rates(self):
        for cxx in range(0, 4):
            for ixx in range(-7, 96000 + 1):

                if ixx in (8000, 12000, 16000, 24000, 48000) and cxx in (1, 2):
                    continue

                if ixx == -5:
                    fsx = -8000
                elif ixx == -6:
                    fsx = sys.maxsize  # TODO: Must be an INT32_MAX
                elif ixx == -7:
                    fsx = -1 * (sys.maxsize - 1)  # TODO: Must be an INT32_MIN
                else:
                    fsx = ixx

                try:
                    opuslib_next.api.encoder.create_state(
                        fsx, cxx, opuslib_next.APPLICATION_VOIP)
                except opuslib_next.OpusError as exc:
                    self.assertEqual(exc.code, opuslib_next.BAD_ARG)

    def test_create(self):
        try:
            opuslib_next.api.encoder.create_state(48000, 2, opuslib_next.AUTO)
        except opuslib_next.OpusError as exc:
            self.assertEqual(exc.code, opuslib_next.BAD_ARG)

        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_VOIP)
        opuslib_next.api.encoder.destroy(enc)

        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_RESTRICTED_LOWDELAY)
        # TODO: rewrite that code
        # i = opuslib.api.encoder.encoder_ctl(
        #     enc, opuslib.api.ctl.get_lookahead)
        # if(err!=OPUS_OK || i<0 || i>32766)test_failed();
        opuslib_next.api.encoder.destroy(enc)

        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)
        # TODO: rewrite that code
        # i = opuslib.api.encoder.encoder_ctl(
        #     enc, opuslib.api.ctl.get_lookahead)
        # err=opus_encoder_ctl(enc,OPUS_GET_LOOKAHEAD(&i));
        # if(err!=OPUS_OK || i<0 || i>32766)test_failed();
        opuslib_next.api.encoder.destroy(enc)

    @classmethod
    def test_encode(cls):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)
        data = b'\x00' * ctypes.sizeof(ctypes.c_short) * 2 * 960
        opuslib_next.api.encoder.encode(enc, data, 960, len(data))
        opuslib_next.api.encoder.destroy(enc)

    @classmethod
    def test_encode_float(cls):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)
        data = b'\x00' * ctypes.sizeof(ctypes.c_float) * 2 * 960
        opuslib_next.api.encoder.encode_float(enc, data, 960, len(data))
        opuslib_next.api.encoder.destroy(enc)

    def test_unimplemented(self):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)
        try:
            opuslib_next.api.encoder.encoder_ctl(enc, opuslib_next.api.ctl.unimplemented)
        except opuslib_next.OpusError as exc:
            self.assertEqual(exc.code, opuslib_next.UNIMPLEMENTED)

        opuslib_next.api.encoder.destroy(enc)

    def test_application(self):
        self.check_setget(
            opuslib_next.api.ctl.set_application,
            opuslib_next.api.ctl.get_application,
            (-1, opuslib_next.AUTO),
            (opuslib_next.APPLICATION_AUDIO,
             opuslib_next.APPLICATION_RESTRICTED_LOWDELAY)
        )

    def test_bitrate(self):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)

        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_bitrate, 1073741832)

        value = opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_bitrate)
        self.assertLess(value, 700000)
        self.assertGreater(value, 256000)

        opuslib_next.api.encoder.destroy(enc)

        self.check_setget(
            opuslib_next.api.ctl.set_bitrate,
            opuslib_next.api.ctl.get_bitrate,
            (-12345, 0),
            (500, 256000)
        )

    def test_force_channels(self):
        self.check_setget(
            opuslib_next.api.ctl.set_force_channels,
            opuslib_next.api.ctl.get_force_channels,
            (-1, 3),
            (1, opuslib_next.AUTO)
        )

    def test_bandwidth(self):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)

        # Set bandwidth
        ixx = -2
        self.assertRaises(
            opuslib_next.OpusError,
            lambda: opuslib_next.api.encoder.encoder_ctl(
                enc, opuslib_next.api.ctl.set_bandwidth, ixx)
        )

        ix1 = opuslib_next.BANDWIDTH_FULLBAND + 1
        self.assertRaises(
            opuslib_next.OpusError,
            lambda: opuslib_next.api.encoder.encoder_ctl(
                enc, opuslib_next.api.ctl.set_bandwidth, ix1)
        )

        ix2 = opuslib_next.BANDWIDTH_NARROWBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_bandwidth, ix2)

        ix3 = opuslib_next.BANDWIDTH_FULLBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_bandwidth, ix3)

        ix4 = opuslib_next.BANDWIDTH_WIDEBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_bandwidth, ix4)

        ix5 = opuslib_next.BANDWIDTH_MEDIUMBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_bandwidth, ix5)

        # Get bandwidth
        value = opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_bandwidth)
        self.assertIn(
            value,
            (opuslib_next.BANDWIDTH_FULLBAND,
             opuslib_next.BANDWIDTH_MEDIUMBAND,
             opuslib_next.BANDWIDTH_WIDEBAND,
             opuslib_next.BANDWIDTH_NARROWBAND,
             opuslib_next.AUTO)
        )

        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_bandwidth, opuslib_next.AUTO)

        opuslib_next.api.encoder.destroy(enc)

    def test_max_bandwidth(self):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)

        i = -2
        self.assertRaises(
            opuslib_next.OpusError,
            lambda: opuslib_next.api.encoder.encoder_ctl(
                enc, opuslib_next.api.ctl.set_max_bandwidth, i)
        )
        i = opuslib_next.BANDWIDTH_FULLBAND + 1
        self.assertRaises(
            opuslib_next.OpusError,
            lambda: opuslib_next.api.encoder.encoder_ctl(
                enc, opuslib_next.api.ctl.set_max_bandwidth, i)
        )
        i = opuslib_next.BANDWIDTH_NARROWBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_max_bandwidth, i)
        i = opuslib_next.BANDWIDTH_FULLBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_max_bandwidth, i)
        i = opuslib_next.BANDWIDTH_WIDEBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_max_bandwidth, i)
        i = opuslib_next.BANDWIDTH_MEDIUMBAND
        opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.set_max_bandwidth, i)

        i = -12345
        value = opuslib_next.api.encoder.encoder_ctl(
            enc, opuslib_next.api.ctl.get_max_bandwidth)

        self.assertIn(
            value,
            (opuslib_next.BANDWIDTH_FULLBAND,
             opuslib_next.BANDWIDTH_MEDIUMBAND,
             opuslib_next.BANDWIDTH_WIDEBAND,
             opuslib_next.BANDWIDTH_NARROWBAND,
             opuslib_next.AUTO)
        )

        opuslib_next.api.encoder.destroy(enc)

    def test_dtx(self):
        self.check_setget(
            opuslib_next.api.ctl.set_dtx, opuslib_next.api.ctl.get_dtx, (-1, 2), (1, 0))

    def test_complexity(self):
        self.check_setget(
            opuslib_next.api.ctl.set_complexity,
            opuslib_next.api.ctl.get_complexity,
            (-1, 11),
            (0, 10)
        )

    def test_inband_fec(self):
        self.check_setget(
            opuslib_next.api.ctl.set_inband_fec,
            opuslib_next.api.ctl.get_inband_fec,
            (-1, 3),
            (1, 0)
        )

    def test_packet_loss_perc(self):
        self.check_setget(
            opuslib_next.api.ctl.set_packet_loss_perc,
            opuslib_next.api.ctl.get_packet_loss_perc,
            (-1, 101),
            (100, 0)
        )

    def test_vbr(self):
        self.check_setget(
            opuslib_next.api.ctl.set_vbr, opuslib_next.api.ctl.get_vbr, (-1, 2), (1, 0))

    def test_vbr_constraint(self):
        self.check_setget(
            opuslib_next.api.ctl.set_vbr_constraint,
            opuslib_next.api.ctl.get_vbr_constraint,
            (-1, 2),
            (1, 0)
        )

    def test_signal(self):
        self.check_setget(
            opuslib_next.api.ctl.set_signal,
            opuslib_next.api.ctl.get_signal,
            (-12345, 0x7FFFFFFF),
            (opuslib_next.SIGNAL_MUSIC, opuslib_next.AUTO)
        )

    def test_lsb_depth(self):
        self.check_setget(
            opuslib_next.api.ctl.set_lsb_depth,
            opuslib_next.api.ctl.get_lsb_depth,
            (7, 25),
            (16, 24)
        )

    def check_setget(self, v_set, v_get, bad, good):
        enc = opuslib_next.api.encoder.create_state(
            48000, 2, opuslib_next.APPLICATION_AUDIO)

        for value in bad:
            self.assertRaises(
                opuslib_next.OpusError,
                lambda: opuslib_next.api.encoder.encoder_ctl(enc, v_set, value)
            )

        for valuex in good:
            opuslib_next.api.encoder.encoder_ctl(enc, v_set, valuex)
            result = opuslib_next.api.encoder.encoder_ctl(enc, v_get)
            self.assertEqual(valuex, result)

        opuslib_next.api.encoder.destroy(enc)
