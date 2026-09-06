<p align="center">
  <img alt="Progress Quest" src="http://progressquest.com/pq.png">
</p>

*[English](README.md) | 日本語*

あの偉大な冒険をもう一度……今度はターミナルの世界で！

- Progress Quest 公式サイト: http://progressquest.com/
- オンライン版:              http://progressquest.com/play/
- オリジナル版:              https://bitbucket.org/grumdrig/pq

このリポジトリは Laura Kurczewska 氏による
[rr-/pq-cli](https://github.com/rr-/pq-cli) のフォークです。日本語化と、
地の文だけでなくゲーム全体を翻訳可能にする仕組みを追加しています。
原作の MIT ライセンスと著作権表示は `LICENSE.md` にそのまま残してあります。

## 特徴

- ゲームロジックを忠実に移植
- セーブデータ（バックアップ付き）は `$XDG_CONFIG_HOME/pqcli/save.dat` に保存
- ターミナルインターフェースは2種類:
    - 華やかでカラフルな表示（`--curses`、デフォルト）
    - ひたすら放置に適した最小限の表示（`--basic`）
- サーバーで動かしっぱなしにするのに最適
- 英語・日本語の表示に対応

## 画面イメージ

curses インターフェース:

![スクリーンショット](https://raw.githubusercontent.com/hannibal414/pq-cli/main/screen-curses-logo-ja.png)
![スクリーンショット](https://raw.githubusercontent.com/hannibal414/pq-cli/main/screen-curses-ja.png)

basic インターフェース:

![スクリーンショット](https://raw.githubusercontent.com/hannibal414/pq-cli/main/screen-basic-ja.png)

## インストール方法

Python 3.10 以降があれば `pip install --user pqcli-ja` を実行するだけです。
あとは `pqcli` と入力すればゲームが始まります。

これは日本語版で、PyPI では `pqcli-ja` という名前で公開しています。
オリジナルの英語版は `pqcli` という別のパッケージです。どちらも `pqcli`
というコマンドを入れるので、同じ環境には片方だけをインストールしてください。

git 版を使いたい場合は、もう少しだけ手順が増えます:

```console
$ git clone https://github.com/hannibal414/pq-cli.git
$ cd pq-cli
$ pip install --user .
```

## Docker / Docker Compose

このリポジトリには `Dockerfile` と `docker-compose.yml` が含まれており、
`--basic` でゲームを起動し、セーブデータを永続的な名前付きボリュームに
保持します。

レジストリを用意する必要はありません。ローカルでビルドして Compose で
実行してください。

```console
# Dockerfile からローカルでイメージをビルド
docker compose build

# 初回実行（対話モード）: 共有ボリューム内にキャラクターを作成する
docker compose run --rm pqcli-init

# 以降のサーバー実行（デタッチモード、デフォルトのセーブスロット1）:
docker compose up -d pqcli

# 同じボリューム内の既存セーブを一覧表示:
docker compose run --rm pqcli-init pqcli --basic --list-saves

# 必要ならデタッチ実行時のスロットを変更（例: スロット2）:
PQCLI_SAVE_SLOT=2 docker compose up -d pqcli

# ログの追跡 / デタッチ実行中のコンテナの停止:
docker compose logs -f pqcli
docker compose stop pqcli
```

初回実行時、マウントされたボリュームにセーブデータが存在しない場合、
`pqcli` は通常のインターフェースを起動する前に、CLIモードで対話的な
キャラクター作成を自動的に開始します。

サーバーで運用する場合は、まずスロットを指定せずに初回セットアップ
（`pqcli-init`）を実行し、その後デフォルトでスロット `1` を読み込む
常駐サービス（`pqcli`）を起動してください。

## 言語

このゲームには英語（ソース言語）と日本語が同梱されています。
`PQCLI_LANG` 環境変数で切り替えます:

```console
PQCLI_LANG=ja pqcli
PQCLI_LANG=en pqcli
```

`PQCLI_LANG` が未設定の場合は、通常の gettext 環境変数
（`LANGUAGE`、`LC_ALL`、`LC_MESSAGES`、`LANG`）が参照されます。
該当するカタログが見つからない場合は英語にフォールバックします。

画面に出るものはすべて翻訳できます。`pqcli/config.py` のゲームデータ
（モンスター名・呪文名・種族名・クラス名・アイテム名・装備名）も対象です。
そこにある英語文字列は表示用ではなく**識別子**で、コードとセーブファイルと
msgid が共有する唯一の名前です。表示は描画時にカタログを引いて解決されるので、
翻訳するときは msgstr を追加するだけで、`pqcli/config.py` を書き換えては
いけません。

テキストは完成した文ではなく**フレーズ**（`pqcli/text.py`）、つまり msgid と
差し込みパラメータの組で保存されます。そのため言語を切り替えると既存の
セーブに記録済みのテキストにも反映され、翻訳者は `.po` 側で語順を
入れ替えられます。フレーズ導入以前のバージョンが書いたテキストだけは、
元の msgid を復元できないため生成時の言語のまま残ります。

英文法（冠詞・複数形・形容詞の前置）は `pqcli/lingo/en.py` にあります。
`pqcli/lingo/__init__.py` が有効なカタログからバックエンドを選び、無ければ
英語にフォールバックします。`pqcli/lingo/<言語>.py` を足すのが、その言語に
固有の文法規則を持たせる方法です。

### 翻訳の追加・更新

翻訳作業には開発用の依存関係が必要です（`uv sync`）。

```console
# 1. ソースから msgid を再抽出して .pot テンプレートを更新する
uv run pybabel extract -F babel.cfg -k N_ -k Term -k phrase \
    -o pqcli/locale/pqcli.pot \
    --project=pqcli --version=1.1.0 \
    --copyright-holder="pq-cli contributors" \
    --msgid-bugs-address="https://github.com/hannibal414/pq-cli/issues" .

# 2. テンプレートを既存のカタログにマージする
uv run pybabel update -i pqcli/locale/pqcli.pot -d pqcli/locale -D pqcli

# 3. pqcli/locale/<言語>/LC_MESSAGES/pqcli.po を編集し、.mo にコンパイルする
uv run pybabel compile -d pqcli/locale -D pqcli --statistics
```

新しい言語を追加する場合（例として `de`）:

```console
uv run pybabel init -i pqcli/locale/pqcli.pot -d pqcli/locale -l de -D pqcli
```

ゲームが実行時に読み込むのはコンパイル済みの `.mo` ファイルです。
`.po` を編集したら必ず手順3を再実行してください。pre-commit の
`compile-catalogs` フックが `.po` の変更時に自動で実行します。

`.mo` はビルド生成物で git 管理外です。`hatch_build.py` が wheel と sdist に
コンパイルして格納します。そのため翻訳の pull request には編集した `.po` だけが
含まれ、バイナリは入らず、レビュー中に古くなるものもありません。

ゲームデータを抽出しているのは `-k N_ -k Term -k phrase` です。`N_()` は
`pqcli/config.py` の文字列をその場で翻訳せずに抽出対象として印を付け、
`Term()` は利用箇所でその文字列を指し、`phrase()` は遅延評価される文を
組み立てます。

ソースに翻訳対象の文字列を追加するときは `pqcli.i18n` の `_()` で
囲みます。その際、文字列連結ではなく `.format()` を使った1文まるごとの
msgid にしてください。日本語のように語順が異なる言語でも、翻訳者が
語順を入れ替えられるようにするためです:

```python
# 良い例 -- msgid が1つで、プレースホルダを移動できる
_("Selling {item}").format(item=indefinite(item.name, item.quantity))

# 悪い例 -- 語順がコード側に固定されてしまう
_("Selling ") + indefinite(item.name, item.quantity)
```

`_` は gettext の関数である点に注意してください。これを import している
モジュール内で、使い捨ての変数名として `_` を使わないでください
（`for _ in range(...)` など）。gettext の `_` を上書きしてしまいます。

### 表示が変わっていないことの確認

テストが無いため、`tools/golden.py` がその代わりになります。シードを固定した
5本のシミュレーションを走らせ、表示される文字列をすべてダンプします。
`--check` で `tools/golden_expected.txt` と突き合わせ、差分があれば失敗します。
差分を読んだうえで意図した変更なら `--update` で記録し直してください。
pre-commit の `golden-output` フックが自動で確認します。翻訳作業では英語の
ダンプは変わらないので、このフックは静かなままで、コードを変えたときだけ
反応します。

## 開発への参加

翻訳に必要なのは `.po` エディタだけです。[CONTRIBUTING.ja.md](CONTRIBUTING.ja.md) を参照してください。
コードを変更する場合:

```sh
# リポジトリをクローン:
git clone https://github.com/hannibal414/pq-cli.git
cd pq-cli

# ローカルの venv に依存関係をインストール:
uv sync

# pre-commit フックをインストール:
uv run pre-commit install

# カタログを一度コンパイルする（英語以外で起動するために必要。
# 以降はフックが最新に保ちます）:
uv run pybabel compile -d pqcli/locale -D pqcli

# コマンドを venv 内で実行:
uv run pqcli
```

このプロジェクトはパッケージ管理に [uv](https://docs.astral.sh/uv/) を
使用しています。インストール手順は
[uv のインストールガイド](https://docs.astral.sh/uv/getting-started/installation/)
を参照してください。

## トラブルシューティング

### `_curses.error: init_pair() returned ERR`

Linux で実行時に `_curses.error: init_pair() returned ERR` というエラーが
出る場合は、`$TERM` 環境変数が256色に対応した値になっているか確認して
ください。例えば次のように指定します:

    TERM=xterm-256color pqcli

### 日本語が正しく表示されない・レイアウトが崩れる

日本語表示には、全角文字を扱えるターミナルと UTF-8 ロケールが必要です。
文字化けやレイアウトの崩れが起きる場合は、次を確認してください:

- ターミナルの文字コードが UTF-8 になっているか
- `$TERM` が 256色対応の値（`xterm-256color` など）になっているか
- 日本語グリフを含むフォントが設定されているか

curses インターフェースは全角文字の幅を考慮してレイアウトを計算します
（`pqcli/ui/curses/util.py` の `display_width()`）が、
ターミナル側が全角文字を半角幅で描画する設定になっていると、
枠線がずれることがあります。
