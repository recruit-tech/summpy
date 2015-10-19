#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import re
import json
import subprocess

import MeCab


def tree_encode(obj, encoding='utf-8'):
    type_ = type(obj)
    if type_ == list or type_ == tuple:
        return [tree_encode(e, encoding) for e in obj]
    elif type_ == dict:
        new_obj = dict(
            (tree_encode(k, encoding), tree_encode(v, encoding))
            for k, v in obj.iteritems()
        )
        return new_obj
    elif type_ == unicode:
        return obj.encode(encoding)
    else:
        return obj


def ppj(obj, sort_keys=False):
    obj_str = json.dumps(
        tree_encode(obj), indent=2, ensure_ascii=False, sort_keys=sort_keys
    )
    print obj_str


# ここからmecab関連

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


def _node2word(n):  # <- mecab node
    return n._surface


def _node2norm_word(n):  # mecab node
    if n.feat_dict['orig'] != '*':
        return n.feat_dict['orig']
    else:
        return n._surface


def word_segmenter_ja(sent, node_filter=not_stopword,
                      node2word=_node2norm_word, mecab_encoding='utf-8'):
    if type(sent) == unicode:
        sent = sent.encode(mecab_encoding)

    nodes = list(
        _mecab_node2seq(_mecab.parseToNode(sent), mecab_encoding=mecab_encoding)
    )
    if node_filter:
        nodes = [n for n in nodes if node_filter(n)]
    words = [node2word(n) for n in nodes]

    return words


def fix_paren_sents(sents):
    '''
    sent_splitter_jaでは、
    "太郎は「明日は晴れるだろう。」といった。"
        -> ["太郎は「明日は晴れるだろう。", "」といった。"]
    に分割される。

    この関数はカッコの対応を見て、文を境界を修正する。
    exmaple:
      sents = ["太郎は「明日は晴れるだろう。", "」といった。"]
      returns ["太郎は「明日は晴れるだろう。」といった。"]
    '''
    # 開いた括弧は必ず閉じる．
    # 全角（） -> 半角()
    sents = [s.replace(u'（', u'(').replace(u'）', u')') for s in sents]
    parenthesis = u'（）「」『』()'
    close2open = dict(zip(parenthesis[1::2], parenthesis[0::2]))
    fixed_sents = []
    pstack = []
    buff = u''
    for sent in sents:
        pattern = re.compile(u'[' + parenthesis + u']')
        ps = re.findall(pattern, sent)
        if len(ps) > 0:
            for p in ps:
                if p in close2open.values():
                    # open
                    pstack.append(p)
                elif len(pstack) > 0 and pstack[-1] == close2open[p]:
                    # close
                    pstack.pop()
        # ここでpstackが空なら括弧の対応がとれている．
        if len(pstack) == 0:
            buff += sent
            if len(buff) > 0:
                fixed_sents.append(buff)
            buff = u''
        else:
            buff += sent
    if len(buff) > 0:
        fixed_sents.append(buff)

    return fixed_sents


def sent_splitter_ja(text, fix_paren=True):  # type(text) == unicode
    sents = re.sub(ur'([。．？！\n\r]+)', r'\1|', text).split('|')
    sents = [s for s in sents if len(s) > 0]
    if fix_paren:
        sents = fix_paren_sents(sents)
    return sents


def test_mecab():
    text = u'今日はいい天気ですね。太郎は今日学校に行こうとしています。'
    sents = sent_splitter_ja(text)
    for s in sents:
        ws = word_segmenter_ja(s)
        print '|'.join(ws)


def l2norm(xs):
    return math.sqrt(sum(x * x for x in xs))


def cos_sim(v1, v2):
    if len(v1) == 0 or len(v2) == 0:
        return 0
    a = 0
    for k in v1:
        a += v1[k] * (v2[k] if k in v2 else 0)
    b = l2norm(v1.values()) * l2norm(v2.values())
    return a / b


if __name__ == '__main__':
    test_mecab()
