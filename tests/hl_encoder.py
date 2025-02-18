#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

"""Tests for a high-level Decoder object"""

import unittest

import opuslib_next

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


class EncoderTest(unittest.TestCase):

    def test_create(self):
        try:
            opuslib_next.Encoder(1000, 3, opuslib_next.APPLICATION_AUDIO)
        except opuslib_next.OpusError as ex:
            self.assertEqual(ex.code, opuslib_next.BAD_ARG)

        opuslib_next.Encoder(48000, 2, opuslib_next.APPLICATION_AUDIO)

    @classmethod
    def test_reset_state(cls):
        encoder = opuslib_next.Encoder(48000, 2, opuslib_next.APPLICATION_AUDIO)
        encoder.reset_state()
