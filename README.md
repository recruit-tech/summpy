# Summpy

Text summarization (sentence extraction) module for Python.
(Currently summpy supports Japanese only)

## License

MIT License (See a License file)

## Requirements 

### Python 2.7.*

+ numpy
+ networkx
+ scikit-learn
+ cherrypy
+ MeCab
+ pulp (if you use 'algo=mcp')

## Quick start

```sh
git clone XXX
cd summpy
python api/server.py -h localhost -p 8080
curl http://localhost:8080/summarize\?sent_limit\=3\&text\=要約したい文章を入力。
```

### Input Parameters

- `text`: (required) text (utf-8, you want to summarize) 
- `algo`: (optional) < lexrank | clexrank | mcp >
  + `lexrank`: LexRank, a graph-based summarization (default)
  + `clexrank`: Continuous LexRank (see reference)
  + `mcp`: Extracts sentences in terms of Maximum Coverage Problem.

Hyper parameters for how many sentences are shown (optional) 

- `sent_limit`: number of sentences (only lexrank)
- `char_limit`: number of characters
- `imp_require`: cumulative LexRank scores \[0.0-1.0\] (only lexrank)

### Example

from ([http://blog.recruit-tech.co.jp/2015/08/28/recruit_two_cx/](http://blog.recruit-tech.co.jp/2015/08/28/recruit_two_cx/))

#### Request

```sh
curl http://localhost:8080/summarize\?sent_limit\=3\&text\=突然ですが、リクルートのリボンモデルを耳にしたことはあるでしょうか？リボンモデルは2003年頃に当時は情報誌やフリーペーパーを主体としたメディアやビジネスを構築・実現するための基本構想として誕生し、ネットモデルへのトランスフォメーションを通じてその後、リクルート内で広まっていきました。リクルートが提供する多くのサービスが後に言及するカスタマーとクライアント双方のマッチングを実現するサービスと称される背景にはこのリボンモデルがあります。リボンモデルはいまでは社内における共通言語として浸透し、語られています。故に、これからも当ブログでは何度もこのリボンモデルが登場すると思います。リボンモデルは、部署や専門領域が異なるも、論点を明確に示す、いわばコンパスのような役割を果たします。例えば、集客を基軸とした施策立案や検討を目的とした議論の際はカスタマーの裾の部分。コンバージョンなど意思決定に関わる施策検討に関する議論の場合はリボンの結びの部分、というように全体の縮図から対象の領域を特定することでマクロな観点での分析や影響因子を推測することが可能になります。リクルートテクノロジーズではUX（ユーザエクスペリエンス）の観点から、このリボン構造を踏まえたマッチングを基軸としたUXデザインを支援・遂行しています。そしてこのリボンモデルこそ、リクルートにおけるUXデザインそのもの、とも言えることができます。UXデザインはその背景思想となる人間中心設計（ユーザー中心設計）の国際規格で1999年に発行されたISO13407をきっかけに、日本では2003年頃より普及し始めました。リボンモデル構想が生まれた年と偶然一致します。2010年にはその規格が改訂され、国際規格としてUXが定義されました。その定義によれば、「ユーザエクスペリエンスには、使用前、使用中、使用後に生じるユーザの感情、信念、嗜好、知覚、生理学的・心理学的な反応、行動や達成の全てを含む」と記載されています。リボンモデルは国際規格の普及によって生まれた構想ではないものの、リボンモデルの構造はカスタマーとクライアントの体験設計基盤とも捉えることができ、UXデザインの普及・浸透と足並を揃えるかのように組織内に醸成されていきました。リボンモデルが目指すCX思想は大きく分けて2つあります。1.CustomerExperience:カスタマーエクスペリエンスの向上（アクション創出の最大化）2.ClientExperience:クライアントエクスペリエンスの向上（期待価値の最大化）双方のUX、リクルートでは双方のCX（カスタマー＆クライアントエクスペリエンス）を配慮したサービスデザインが求められます。このように、リボンモデルは両者の視点を交えて両者をつなぐためのUXデザインフレームワークとも捉えることができます。例えば当方が関わっているサービスにおいては以下のように体験を前述の定義に従って分解することができます。また、KPIも分解された各アクションごとに設計・設計し、モニタリングする仕組みを構築しています。本来、UXが指し示す「U」はカスタマーのみに限定されず、サービスを構成する様々なステークホルダーをも対象としたトータルデザインが求められます。リクルートでは、偶然にもUXデザインと同時期に普及したこのリボンモデルによって、構想段階に留まらず、実現に向けたアクションをカスタマーとクライアントエクスペリエンスの観点からブレイクダウンすることで、両者を結び、最高の体験を提供するためのサービスないしはビジネスの実現を目指しています。結果としてユーザーとの対立構造が象徴されるWIN-WINな関係ではなく、サービスを共に創造していくためのクライアントを含めたWIN-WIN-WINの関係性を築くことで、双方にとっての「まだ、ここにない、出会い」を生み出す、文字通りのサービスデザインを実践することができます。スクリーンの前でこの記事を読まれているあなたも、共に「まだ、ここにない、出会い」を探しに、見つけに、そして生み出しにいきませんか？
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

#### Try with browser

`http://<hostname>:<port>/static/test.html`

## Use summpy in your Python application

### Install

```sh
pip install path/to/summpy
```

### Example (clexrank)

```python
from summpy.lexrank import summarize

# ensure type(text) is unicode
sentences, debug_info = summarize(
    text, sent_limit,
    debug=True, continuous=True
)

for sent in sentences:
    print sent.strip().encode(encoding)
```

For further details, see `main` part of `summpy/lexrank.py` or `mcp_summ.py`.

## References

- `lexrank.py` ([LexRank](http://www.cs.cmu.edu/afs/cs/project/jair/pub/volume22/erkan04a-html/erkan04a.html), section 3)
- `mcp_summ.py` ([Takamura 2009](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.222.6945), section 3)
