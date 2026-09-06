# 開発・翻訳への参加

*[English](CONTRIBUTING.md) | 日本語*

貢献の種類によって必要な準備が大きく違うので、目的に合う方を読んでください。

## 翻訳する

必要なのは `.po` エディタだけです。Python もビルドツールも要りません。
[Poedit](https://poedit.net/) は無料で Windows・macOS・Linux で動きます。
普通のテキストエディタでも構いません。

1. `pqcli/locale/<言語>/LC_MESSAGES/pqcli.po` を開きます。日本語なら
   `pqcli/locale/ja/LC_MESSAGES/pqcli.po` です。
2. 訳したい `msgstr` を埋めます。
3. その `.po` だけを含む pull request を送ります。

これで全部です。**コンパイルは不要**です。`.mo` はビルド生成物で git 管理外、
リリースをビルドする時に生成されます。

途中まででも歓迎します。未訳の項目は英語にフォールバックするので、10件だけ
訳して止めてもゲームは問題なく遊べます。現時点で日本語は 982 件中 207 件です。

### 何を訳すことになるか

100件ほどが UI のラベルと文の骨格で、残りはゲームデータ（モンスター名・呪文名・
種族名・クラス名・アイテム名・装備名）です。本番はこちらで、Progress Quest は
RPG のパロディなので中身は言葉遊びです。`Cone of Annoyance`、`Slime Finger`、
`Battle-Ghoul` といった調子で、笑いを他言語で保つのは翻訳というより創作です。
直訳より「面白さが伝わる名前」を優先してください。同じ名前は出現箇所すべてで
統一してください。

文の骨格は `Executing {monster}` のような形です。`{...}` は残したまま、
日本語として自然な位置に動かして構いません。語順を入れ替えられるようにするために
文字列連結ではなくプレースホルダにしてあります。

### `pqcli/config.py` は編集しないでください

このファイルの英語文字列は表示用ではなく**識別子**です。コードもセーブファイルも
msgid も、すべてこの文字列を共通の名前として参照しています。ここを書き換えると
全カタログとの対応が壊れます。翻訳は必ず `msgstr` の追加で行ってください。

### 新しい言語を追加する

```console
uv run pybabel init -i pqcli/locale/pqcli.pot -d pqcli/locale -l de -D pqcli
```

言語によっては、カタログだけでは表現できない文法（冠詞・複数形・助数詞・形容詞の
位置）が必要になります。それは `pqcli/lingo/<言語>.py` に書き、
`pqcli/lingo/__init__.py` の `_BACKENDS` に登録します。**自分の言語で実際に
異なる規則だけ**を定義すれば十分で、それ以外は英語にフォールバックします。
関数2つだけのバックエンドでも動きます。

## コードを変更する

```console
git clone https://github.com/hannibal414/pq-cli.git
cd pq-cli
uv sync
uv run pre-commit install

# 英語以外で起動するために一度だけ実行:
uv run pybabel compile -d pqcli/locale -D pqcli

uv run pqcli
```

テストスイートはありません。代わりに `tools/golden.py` があります。シードを
固定した5本のシミュレーションを走らせて表示される文字列をすべてダンプし、
`golden-output` フックが `tools/golden_expected.txt` と突き合わせます。

差分が出ても即バグとは限りません。それは**あなたの変更が表示に与えた影響の
一覧**です。読んだうえで意図どおりなら記録し直してください。

```console
uv run python tools/golden.py --update
```

翻訳作業でこのダンプが変わることはないので、カタログを編集している間フックは
静かなままです。

### ソースに文字列を追加する

`pqcli.i18n` の `_()` で囲み、文字列を連結せずに**1文まるごとを1つの msgid**に
して名前付きプレースホルダを使ってください。

```python
# 良い例 — msgid が1つで、翻訳者が語順を変えられる
_("Selling {item}").format(item=name)

# 悪い例 — 英語の語順がコードに焼き付く
_("Selling ") + name
```

セーブファイルに保存されるテキストは、描画済みの文字列ではなく `pqcli.text` の
フレーズにしてください。言語切替のあとに再描画できるようにするためです。
`_` は gettext の関数なので、これを import しているモジュールで
使い捨て変数名（`for _ in range(...)`）として使わないでください。

## 本家について

このリポジトリは [rr-/pq-cli](https://github.com/rr-/pq-cli) のフォークです。
日本語化に関係しない変更は、本家に送った方が良い場合があります。
