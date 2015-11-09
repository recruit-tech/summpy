#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import MeCab


_mecab = MeCab.Tagger()
# 品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
_mecab_feat_labels = 'pos cat1 cat2 cat3 conj conj_t orig read pron'.split(' ')


def _mecab_parse_feat(feat):
    return dict(zip(_mecab_feat_labels, feat.split(',')))


def _mecab_node2seq(node, decode_surface=True, feat_dict=True,
                    mecab_encoding='utf-8'):
    # MeCab.Nodeはattributeを変更できない。
    while node:
        if decode_surface:
            node._surface = node.surface.decode(mecab_encoding)
        if feat_dict:  # 品詞の情報をdictで保存
            node.feat_dict = _mecab_parse_feat(
                node.feature.decode(mecab_encoding)
            )
        yield node
        node = node.next


def is_stopword(n):  # <- mecab node
    if len(n._surface) == 0:
        return True
    elif re.search(ur'^[\s!-@\[-`\{-~　、-〜！-＠［-｀]+$', n._surface):
        return True
    elif re.search(ur'^(接尾|非自立)', n.feat_dict['cat1']):
        return True
    elif u'サ変・スル' == n.feat_dict['conj'] or u'ある' == n.feat_dict['orig']:
        return True
    elif re.search(ur'^(名詞|動詞|形容詞)', n.feat_dict['pos']):
        return False
    else:
        return True


def not_stopword(n):  # <- mecab node
    return not is_stopword(n)


def node2word(n):  # <- mecab node
    return n._surface


def node2norm_word(n):  # mecab node
    if n.feat_dict['orig'] != '*':
        return n.feat_dict['orig']
    else:
        return n._surface


def word_segmenter_ja(sent, node_filter=not_stopword,
                      node2word=node2norm_word, mecab_encoding='utf-8'):
    if type(sent) == unicode:
        sent = sent.encode(mecab_encoding)

    nodes = list(
        _mecab_node2seq(_mecab.parseToNode(sent), mecab_encoding=mecab_encoding)
    )
    if node_filter:
        nodes = [n for n in nodes if node_filter(n)]
    words = [node2word(n) for n in nodes]

    return words


if __name__ == '__main__':
    text = u'今日はいい天気ですね。'
    print '|'.join(word_segmenter_ja(text)).encode('utf-8')
