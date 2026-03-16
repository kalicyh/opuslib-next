#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock

import opuslib_next


class OpusErrorTest(unittest.TestCase):
    def test_str_decodes_libopus_message(self):
        with mock.patch(
            "opuslib_next.api.info.strerror",
            return_value=b"bad argument"
        ):
            self.assertEqual("bad argument", str(opuslib_next.OpusError(-1)))
