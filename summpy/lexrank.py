#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import codecs
import collections
import numpy
import networkx
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import pairwise_distances

import tools


def lexrank(sentences, sim_threshold=.1, alpha=0.9):
    '''
    文の重要度を計算する．

    Args:
      sentences: [u'こんにちは．', u'私の名前は飯沼です．', ... ]
      sim_threshold: 文間の類似度がsim_thresholdなら，エッジを作る．
      alpha: PageRankのダンピングファクタ

    Returns: 文のインデックス -> 重要度 のdict
      {
        0: 0.003,
        1: 0.002,
        ...
      }
    '''
    graph = networkx.DiGraph()

    # sentence -> tf
    sent_tf_list = []
    for sent in sentences:
        words = tools.word_segmenter_ja(sent)
        tf = collections.Counter(words)
        sent_tf_list.append(tf)

    sent_vectorizer = DictVectorizer(sparse=True)
    sent_vecs = sent_vectorizer.fit_transform(sent_tf_list)

    # 文間の類似度を計算，閾値以上のインデックス(行番号，列番号)を求める．
    sim_mat = 1 - pairwise_distances(sent_vecs, sent_vecs, metric='cosine')
    linked_rows, linked_cols = numpy.where(sim_mat >= sim_threshold)

    # グラフ作成
    graph.add_nodes_from(range(sent_vecs.shape[0]))
    for i, j in zip(linked_rows, linked_cols):
        if i == j:
            continue
        graph.add_edge(i, j)

    scores = networkx.pagerank_scipy(graph, alpha=alpha, max_iter=1000)
    return scores, sim_mat


def summarize(text, sent_limit=None, char_limit=None, imp_require=None):
    '''
    Args:
      text: 要約対象の文章 (unicode string)
      sent_limit: 文数制限
      char_limit: 文字数制限
      imp_require: [0.0 - 1.0] 重要度の累積が全体のimp_requireを超えるように文を選択

    Returns:
      文を格納したリスト
    '''
    sentences = tools.sent_splitter_ja(text)
    scores, sim_mat = lexrank(sentences)
    sum_scores = sum(scores.itervalues())
    acc_scores = 0.0
    indexes = set()
    num_sent, num_char = 0, 0
    for i in sorted(scores, key=lambda i: scores[i], reverse=True):
        num_sent += 1
        num_char += len(sentences[i])
        if sent_limit is not None and num_sent > sent_limit:
            break
        if char_limit is not None and num_char > char_limit:
            break
        if imp_require is not None and acc_scores / sum_scores >= imp_require:
            break
        indexes.add(i)
        acc_scores += scores[i]

    if len(indexes) > 0:
        summary_sents = [sentences[i] for i in sorted(indexes)]
    else:
        summary_sents = sentences

    return summary_sents


if __name__ == '__main__':

    _usage = '''
Usage:
    python lexrank.py -f <file_name> [-s <文数制限>] [-c <文字数制限>] [-i <累積重要度>]
    '''.strip()

    options, args = getopt.getopt(sys.argv[1:], 'f:s:c:i:')
    options = dict(options)

    if len(options) < 2:
        print _usage
        sys.exit(0)

    fname = options['-f']
    sent_limit = int(options['-s']) if '-s' in options else None
    char_limit = int(options['-c']) if '-c' in options else None
    imp_require = float(options['-i']) if '-i' in options else None

    if fname == 'stdin':
        text, line = '', ''
        while line != 'EOS':
            line = raw_input().decode('utf-8')
            text += line + '\n'
    else:
        text = codecs.open(fname, encoding='utf-8').read()

    for sent in summarize(text, sent_limit=sent_limit, char_limit=char_limit,
                          imp_require=imp_require):
        print sent.encode('utf-8')
