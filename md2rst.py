#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import pypandoc


f = codecs.open('README.rst', 'w', encoding='utf-8')
f.write(pypandoc.convert('README.md', 'rst'))
f.close()
