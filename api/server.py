#!/usr/bin/env python
# coding: utf-8

import sys
import os
import getopt
import cherrypy
import json

from summpy import tools
from summpy import lexrank
from summpy import mcp_summ


class Summarizer(object):

    @cherrypy.expose
    def summarize(self, text=None, algo=u'lexrank', sent_limit=u'',
                  char_limit=u'', imp_require=u'', mode=u''):
        '''
        Args:
            text: 要約対象テキスト
            algo: 要約アルゴリズム
                - 'lexrank' (default) グラフベースの重要度計算アルゴリズム
                - 'mcp' 最大被覆問題として、できるだけ多くの単語を含むように
                    文を選択する。
                注意: mcpの制約は文字数(char_limit)しか指定できない。
            sent_limit: 文数制限
            char_limit: 文字数制限
            imp_requre: 累積重要度がこれを超えるまで文を選択する。
            mode: lexrankの時'score'を指定すると、文と重要度のペアのリストを返す
        '''
        try:  # TODO try-except を細分化する．
            sent_limit = int(sent_limit) if sent_limit != '' else None
            char_limit = int(char_limit) if char_limit != '' else None
            imp_require = float(imp_require) if imp_require != '' else None

            if algo == 'lexrank':
                if mode == '':  # 重要文抽出
                    sents = lexrank.summarize(
                        text, sent_limit=sent_limit, char_limit=char_limit,
                        imp_require=imp_require
                    )
                elif mode == 'score':  # [(文，重要度), ... ]
                    sentences = tools.sent_splitter_ja(
                        text, fix_parenthesis=True
                    )
                    scores, sim_mat = lexrank.lexrank(sentences)
                    sents = []
                    for i in sorted(scores.keys()):
                        el = (sentences[i], scores[i])
                        sents.append(el)

            elif algo == 'mcp':
                sents = mcp_summ.summarize(text, char_limit)

        except Exception, e:
            return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)
        else:
            res = json.dumps(
                tools.tree_encode(sents), ensure_ascii=False, indent=2
            )
            return res


if __name__ == '__main__':

    options, args = getopt.getopt(sys.argv[1:], 'h:p:')
    options = dict(options)
    host, port = options['-h'], int(options['-p'])

    cherrypy.config.update({
        'server.socket_host': host,
        'server.socket_port': port
    })
    conf = {
        '/': {
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__))
        },
        '/summarize': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [
                ('Content-type', 'application/json')
            ]
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.quickstart(Summarizer(), '/', conf)
