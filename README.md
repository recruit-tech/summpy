# Summpy

Text summarization (sentence extraction) module with simple HTTP API.
(Currently supports Japanese only)

## License

MIT License

## Requirements 

### Python 2.7.*

+ numpy
+ scipy
+ scikit-learn
+ networkx
+ cherrypy
+ MeCab or janome
+ pulp (if you use ILP-based method)

## Quick start

```sh
pip install summpy
python -m summpy.server -h 127.0.0.1 -p 8080
curl http://127.0.0.1:8080/summarize\?sent_limit\=3\&text\=要約したい文章を入力。
```

### Input Parameters

- `text`: text (utf-8)
- `algo`: (optional)
  + `lexrank`: LexRank, a graph-based summarization (default)
  + `clexrank`: Continuous LexRank
  + `divrank`: (experimental) DivRank (Diverse Rank, graph-based method). Since DivRank aims to provide non-redundant and high coverage information, it is suitable for multi-document summarization.
  + `mcp`: ILP-based method. Extracts sentences in terms of Maximum Coverage Problem.

Hyper parameters for how many sentences are shown (optional) 

- `sent_limit`: number of sentences (only {lex,clex,div}rank)
- `char_limit`: number of characters
- `imp_require`: cumulative scores \[0.0-1.0\] (only {lex,clex,div}rank)

### Example

from ([http://blog.recruit-tech.co.jp/2015/08/28/recruit_two_cx/](http://blog.recruit-tech.co.jp/2015/08/28/recruit_two_cx/))

#### Request

```sh
curl http://127.0.0.1:8080/summarize\?sent_limit\=3\&text\=突然ですが、リクルートのリボンモデルを耳にしたことはあるでしょうか？...
```

#### Response (JSON format)

```javascript
{
  summary: [
    "リクルートが提供する多くのサービスが後に言及するカスタマーとクライアント双方のマッチングを実現するサービスと称される背景にはこのリボンモデルがあります。", 
    "そしてこのリボンモデルこそ、リクルートにおけるUXデザインそのもの、とも言えることができます。", 
    "リボンモデルは国際規格の普及によって生まれた構想ではないものの、リボンモデルの構造はカスタマーとクライアントの体験設計基盤とも捉えることができ、UXデザインの普及・浸透と足並を揃えるかのように組織内に醸成されていきました。"
  ],
  debug_info: {}
}
```

### Try with browser

`http://<hostname>:<port>/static/test.html`

## Python API

### Example (Continuous LexRank)

```python
from summpy.lexrank import summarize

# ensure type(text) is unicode
sentences, debug_info = summarize(
    text, sent_limit=5, continuous=True, debug=True
)

for sent in sentences:
    print sent.strip().encode(encoding)
```

For further details, see `main` part of `summpy/lexrank.py` or `mcp_summ.py`.

## References

- G. Erkan and D. Radev. LexRank: graph-based lexical centrality as salience in text summarization. J. Artif. Int. Res. 22(1), pages 457-479, 2004. ([link](http://www.cs.cmu.edu/afs/cs/project/jair/pub/volume22/erkan04a-html/erkan04a.html))
- Q. Mei, J. Guo, and D. Radev. DivRank: the Interplay of Prestige and Diversity in Information Networks. In Proceedings of the 16th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '10), pages 1009-1018, 2010. ([link](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.174.7982))

- H. Takamura and M. Okumura. Text Summarization Model Based on Maximum Coverage Problem and its Variant. In Proceedings of the 12th Conference of the European Chapter of the Association for Computational Linguistics (EACL '09), pages 781-789, 2009. ([link](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.222.6945))
