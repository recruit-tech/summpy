#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import codecs


long_description = ''
if os.path.exists('README.rst'):
    long_description = codecs.open('README.rst', encoding='utf-8').read()

setup(
    name='summpy',
    version='0.2.1',
    description='Text summarization (sentence extraction) module with simple HTTP API. (currently, supports Japanese only)',
    long_description=long_description,
    author='Shumpei IINUMA',
    author_email='shumpei.iinuma@gmail.com',
    license='MIT',
    url='https://github.com/recruit-tech/summpy',
    #download_url='https://github.com/recruit-tech/summpy/tarball/0.2',
    packages=['summpy', 'summpy.misc'],
    package_data={'summpy': ['server_data/*.html']},
    install_requires=[
        'numpy', 'scipy', 'scikit-learn', 'networkx', 'cherrypy'
    ],
    keywords=[
        'automatic summarization',
        'natural language processing'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ]
)
