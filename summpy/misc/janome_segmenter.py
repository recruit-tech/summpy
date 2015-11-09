#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from janome.tokenizer import Tokenizer


tokenizer = Tokenizer()


def is_stopword(n):  # <- mecab node
    if len(n.surface) == 0:
        return True
    elif re.search(ur'^[\s!-@\[-`\{-~　、-〜！-＠［-｀]+$', n.surface):
        return True
    elif re.search(ur'^(接尾|非自立)', n.part_of_speech.split(',')[1]):
        return True
    elif u'サ変・スル' == n.infl_form or u'ある' == n.base_form:
        return True
    elif re.search(ur'^(名詞|動詞|形容詞)', n.part_of_speech.split(',')[0]):
        return False
    else:
        return True


def not_stopword(n):
    return not is_stopword(n)


def node2word(n):  # <- janome token node
    return n.surface


def node2norm_word(n):  # janome token node
    if n.base_form != '*':
        return n.base_form
    else:
        return n.surface


def _decode_janome_token(t, encoding='utf-8'):
    attributes = ('surface', 'base_form', 'part_of_speech', 'infl_form')
    for attr_name in attributes:
        value = getattr(t, attr_name)
        if type(value) == str:
            setattr(t, attr_name, value.decode('utf-8'))
    return t


def word_segmenter_ja(sent, node_filter=not_stopword,
                      node2word=node2norm_word):
    nodes = (_decode_janome_token(t) for t in tokenizer.tokenize(sent))

    if node_filter:
        nodes = [n for n in nodes if node_filter(n)]
    words = [node2word(n) for n in nodes]

    return words


if __name__ == '__main__':
    text = u'今日はいい天気ですね。'
    print '|'.join(word_segmenter_ja(text)).encode('utf-8')
