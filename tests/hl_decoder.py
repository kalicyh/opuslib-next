#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

"""Tests for a high-level Decoder object"""

import unittest

import opuslib

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


class DecoderTest(unittest.TestCase):

    def test_create(self):
        try:
            opuslib.Decoder(1000, 3)
        except opuslib.OpusError as ex:
            self.assertEqual(ex.code, opuslib.BAD_ARG)

        opuslib.Decoder(48000, 2)

    def test_get_bandwidth(self):
        decoder = opuslib.Decoder(48000, 2)
        self.assertEqual(decoder.bandwidth, 0)

    def test_get_pitch(self):
        decoder = opuslib.Decoder(48000, 2)

        self.assertIn(decoder.pitch, (-1, 0))

        packet = bytes([252, 0, 0])
        decoder.decode(packet, frame_size=960)
        self.assertIn(decoder.pitch, (-1, 0))

        packet = bytes([1, 0, 0])
        decoder.decode(packet, frame_size=960)
        self.assertIn(decoder.pitch, (-1, 0))

    def test_gain(self):
        decoder = opuslib.Decoder(48000, 2)

        self.assertEqual(decoder.gain, 0)

        try:
            decoder.gain = -32769
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BAD_ARG)

        try:
            decoder.gain = 32768
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BAD_ARG)

        decoder.gain = -15
        self.assertEqual(decoder.gain, -15)

    @classmethod
    def test_reset_state(cls):
        decoder = opuslib.Decoder(48000, 2)
        decoder.reset_state()

    def test_decode(self):
        decoder = opuslib.Decoder(48000, 2)

        packet = bytes([255, 49])
        for _ in range(2, 51):
            packet += bytes([0])

        try:
            decoder.decode(packet, frame_size=960)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.INVALID_PACKET)

        packet = bytes([252, 0, 0])
        try:
            decoder.decode(packet, frame_size=60)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BUFFER_TOO_SMALL)

        try:
            decoder.decode(packet, frame_size=480)
        except opuslib.OpusError as exc:
            self.assertEqual(exc.code, opuslib.BUFFER_TOO_SMALL)

        try:
            decoder.decode(packet, frame_size=960)
        except opuslib.OpusError:
            self.fail('Decode failed')

    def test_decode_float(self):
        decoder = opuslib.Decoder(48000, 2)
        packet = bytes([252, 0, 0])

        try:
            decoder.decode_float(packet, frame_size=960)
        except opuslib.OpusError:
            self.fail('Decode failed')
