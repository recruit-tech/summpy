#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import codecs


_this_dir = os.path.abspath(os.path.dirname(__file__))
long_description = codecs.open(
    os.path.join(_this_dir, 'README.md'), encoding='utf-8'
).read()

setup(
    name='summpy',
    version='0.2',
    description='Text summarization (sentence extraction) module. (currently, support Japanese only)',
    long_description=long_description,
    packages=['summpy', 'summpy.misc'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    license='MIT',
)
