#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OpusLib Package."""

import setuptools  # type: ignore

__author__ = 'kalicyh <kalicyh@qq.com>'
__copyright__ = 'Copyright (c) 2025, Kalicyh'
__license__ = 'BSD 3-Clause License'


setuptools.setup(
    name='opuslib-next',
    version='1.0.0',
    author='kalicyh',
    author_email='kalicyh@qq.com',
    license='BSD 3-Clause License',
    url='https://github.com/kalicyh/opuslib-next',
    description='Python bindings to the libopus, IETF low-delay audio codec',
    packages=('opuslib', 'opuslib.api'),
    test_suite='tests',
    zip_safe=False,
    tests_require=[
        'coverage >= 4.4.1',
        'nose >= 1.3.7',
    ],
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ),
)
