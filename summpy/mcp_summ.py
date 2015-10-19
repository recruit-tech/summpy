#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import codecs
import collections
import pulp

import tools


def summarize(text, char_limit, sent_len_min=None):
    '''
    最大被覆問題として要約する．

    Args:
      text: 要約対象のテキスト (unicode)
      char_limit: 文字数制限
      sent_len_min: 長さがこれ以下の文は要約に含めない．

    Returns: 要約文のリスト
      [
        u'こんにちは．',
        u'私は飯沼ではありません．',
        ...
      ]
    '''

    sents = tools.sent_splitter_ja(text)

    # pulpの変数はutfじゃないといけない
    words_list = [
        w.encode('utf-8') for s in sents for w in tools.word_segmenter_ja(s)
    ]
    # 単語の重みを計算 tf (w)
    tf = collections.Counter()
    for words in words_list:
        for w in words:
            tf[w] += 1.0

    # 要約に出てきてほしくない文は除外する．
    if sent_len_min is not None:
        sents = [s for s in sents if len(s) > sent_len_min]

    sent_ids = [str(i) for i in range(len(sents))]  # sentence id
    # c
    sent_id2len = dict((id_, len(s)) for id_, s in zip(sent_ids, sents))

    # a: ある単語が文に含まれているか否か
    word_contain = dict()
    for id_, words in zip(sent_ids, words_list):
        word_contain[id_] = collections.defaultdict(lambda: 0)
        for w in words:
            word_contain[id_][w] = 1

    prob = pulp.LpProblem('summarize', pulp.LpMaximize)

    # 変数を設定
    # x
    sent_vars = pulp.LpVariable.dicts('sents', sent_ids, 0, 1, pulp.LpBinary)
    # z
    word_vars = pulp.LpVariable.dicts('words', tf.keys(), 0, 1, pulp.LpBinary)

    # 最初に目的関数を追加する。sum(w*z)
    prob += pulp.lpSum([tf[w] * word_vars[w] for w in tf])

    # 次に制約を追加していく。
    # sum(c*x) <= K
    prob += pulp.lpSum(
        [sent_id2len[id_] * sent_vars[id_] for id_ in sent_ids]
    ) <= char_limit, 'lengthRequirement'
    # sum(a*x) <= z, すべての単語について
    for w in tf:
        prob += pulp.lpSum(
            [word_contain[id_][w] * sent_vars[id_] for id_ in sent_ids]
        ) >= word_vars[w], 'z:{}'.format(w)

    prob.solve()
    # print("Status:", pulp.LpStatus[prob.status])

    sent_indices = []
    for v in prob.variables():
        # print v.name, "=", v.varValue
        if v.name.startswith('sents') and v.varValue == 1:
            sent_indices.append(int(v.name.split('_')[-1]))

    return [sents[i] for i in sent_indices]


if __name__ == '__main__':

    _usage = '''
Usage:
    python mcp_summ.py -f <file_name> -c <文字数制限>
    '''.strip()

    options, args = getopt.getopt(sys.argv[1:], 'f:c:')
    options = dict(options)

    if len(options) < 2:
        print _usage
        sys.exit(0)

    fname = options['-f']
    char_limit = int(options['-c']) if '-c' in options else None

    if fname == 'stdin':
        text, line = '', ''
        while line != 'EOS':
            line = raw_input().decode('utf-8')
            text += line + '\n'
    else:
        text = codecs.open(fname, encoding='utf-8').read()

    for sent in summarize(text, char_limit=char_limit):
        print sent.encode('utf-8')
