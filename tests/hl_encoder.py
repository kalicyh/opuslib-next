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


class EncoderTest(unittest.TestCase):

    def test_create(self):
        try:
            opuslib.Encoder(1000, 3, opuslib.APPLICATION_AUDIO)
        except opuslib.OpusError as ex:
            self.assertEqual(ex.code, opuslib.BAD_ARG)

        opuslib.Encoder(48000, 2, opuslib.APPLICATION_AUDIO)

    @classmethod
    def test_reset_state(cls):
        encoder = opuslib.Encoder(48000, 2, opuslib.APPLICATION_AUDIO)
        encoder.reset_state()
