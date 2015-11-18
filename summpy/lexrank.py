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

from . import tools
from .misc.divrank import divrank, divrank_scipy


def lexrank(sentences, continuous=False, sim_threshold=0.1, alpha=0.9,
            use_divrank=False, divrank_alpha=0.25):
    '''
    compute centrality score of sentences.

    Args:
      sentences: [u'こんにちは．', u'私の名前は飯沼です．', ... ]
      continuous: if True, apply continuous LexRank. (see reference)
      sim_threshold: if continuous is False and smilarity is greater or
        equal to sim_threshold, link the sentences.
      alpha: the damping factor of PageRank and DivRank
      divrank: if True, apply DivRank instead of PageRank
      divrank_alpha: strength of self-link [0.0-1.0]
        (it's not the damping factor, see divrank.py)

    Returns: tuple
      (
        {
          # sentence index -> score
          0: 0.003,
          1: 0.002,
          ...
        },
        similarity_matrix
      )
    
    Reference:
      Günes Erkan and Dragomir R. Radev.
      LexRank: graph-based lexical centrality as salience in text
      summarization. (section 3)
      http://www.cs.cmu.edu/afs/cs/project/jair/pub/volume22/erkan04a-html/erkan04a.html
    '''
    # configure ranker
    ranker_params = {'max_iter': 1000}
    if use_divrank:
        ranker = divrank_scipy
        ranker_params['alpha'] = divrank_alpha
        ranker_params['d'] = alpha
    else:
        ranker = networkx.pagerank_scipy
        ranker_params['alpha'] = alpha

    graph = networkx.DiGraph()

    # sentence -> tf
    sent_tf_list = []
    for sent in sentences:
        words = tools.word_segmenter_ja(sent)
        tf = collections.Counter(words)
        sent_tf_list.append(tf)

    sent_vectorizer = DictVectorizer(sparse=True)
    sent_vecs = sent_vectorizer.fit_transform(sent_tf_list)

    # compute similarities between senteces
    sim_mat = 1 - pairwise_distances(sent_vecs, sent_vecs, metric='cosine')

    if continuous:
        linked_rows, linked_cols = numpy.where(sim_mat > 0)
    else:
        linked_rows, linked_cols = numpy.where(sim_mat >= sim_threshold)

    # create similarity graph
    graph.add_nodes_from(range(sent_vecs.shape[0]))
    for i, j in zip(linked_rows, linked_cols):
        if i == j:
            continue
        weight = sim_mat[i,j] if continuous else 1.0
        graph.add_edge(i, j, {'weight': weight})

    scores = ranker(graph, **ranker_params)
    return scores, sim_mat


def summarize(text, sent_limit=None, char_limit=None, imp_require=None,
              debug=False, **lexrank_params):
    '''
    Args:
      text: text to be summarized (unicode string)
      sent_limit: summary length (the number of sentences)
      char_limit: summary length (the number of characters)
      imp_require: cumulative LexRank score [0.0-1.0]

    Returns:
      list of extracted sentences
    '''
    debug_info = {}
    sentences = list(tools.sent_splitter_ja(text))
    scores, sim_mat = lexrank(sentences, **lexrank_params)
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

    if debug:
        debug_info.update({
            'sentences': sentences, 'scores': scores
        })

    return summary_sents, debug_info


if __name__ == '__main__':

    _usage = '''
Usage:
  python lexrank.py -f <file_name> [-e <encoding> ]
                  [ -v lexrank | clexrank | divrank ]
                  [ -s <sent_limit> | -c <char_limit> | -i <imp_required> ]
  Args:
    -f: plain text file to be summarized
    -e: input and output encoding (default: utf-8)
    -v: variant of LexRank (default is 'lexrank')
    -s: summary length (the number of sentences)
    -c: summary length (the number of charactors)
    -i: cumulative LexRank score [0.0-1.0]
    '''.strip()

    options, args = getopt.getopt(sys.argv[1:], 'f:e:v:s:c:i:')
    options = dict(options)

    if len(options) < 2:
        print _usage
        sys.exit(0)

    fname = options['-f']
    encoding = options['-e'] if '-e' in options else 'utf-8'
    variant = options['-v'] if '-v' in options else 'lexrank'
    sent_limit = int(options['-s']) if '-s' in options else None
    char_limit = int(options['-c']) if '-c' in options else None
    imp_require = float(options['-i']) if '-i' in options else None

    if fname == 'stdin':
        text = '\n'.join(
            line for line in sys.stdin.readlines()
        ).decode(encoding)
    else:
        text = codecs.open(fname, encoding=encoding).read()

    lexrank_params = {}
    if variant == 'clexrank':
        lexrank_params['continuous'] = True
    if variant == 'divrank':
        lexrank_params['use_divrank'] = True

    sentences, debug_info = summarize(
        text, sent_limit=sent_limit, char_limit=char_limit,
        imp_require=imp_require, **lexrank_params
    )
    for sent in sentences:
        print sent.strip().encode(encoding)
