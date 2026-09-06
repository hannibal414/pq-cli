<p align="center">
  <img alt="Progress Quest" src="http://progressquest.com/pq.png">
</p>

*[English](README.md) | 日本語*

あの偉大な冒険をもう一度……今度はターミナルの世界で！

- Progress Quest 公式サイト: http://progressquest.com/
- オンライン版:              http://progressquest.com/play/
- オリジナル版:              https://bitbucket.org/grumdrig/pq

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

![スクリーンショット](screen-curses-logo.png)
![スクリーンショット](screen-curses.png)

basic インターフェース:

![スクリーンショット](screen-basic.png)

## インストール方法

Python 3.10 以降があれば `pip install --user pqcli` を実行するだけです。
あとは `pqcli` と入力すればゲームが始まります。

git 版を使いたい場合は、もう少しだけ手順が増えます:

```console
$ git clone https://github.com/rr-/pq-cli.git
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

翻訳対象は地の文のみです（UIラベル、行動の説明文、クエスト文、ログ
メッセージ）。ゲーム内の固有名詞（モンスター名・呪文名・種族名・
クラス名・アイテム名・装備名。いずれも `pqcli/config.py` で定義）は
意図的に英語のまま残してあります。それらを活用する `pqcli/lingo.py` の
英文法処理も同様です。

なお、クエスト文や行動の説明文は*生成された時点で*翻訳され、その後
セーブファイルに保存されます。既存のセーブに記録済みのテキストは
生成時の言語のまま残り、言語を切り替えても新しく生成される
テキストにのみ反映されます。

### 翻訳の追加・更新

翻訳作業には開発用の依存関係が必要です（`uv sync`）。

```console
# 1. ソースから msgid を再抽出して .pot テンプレートを更新する
uv run pybabel extract -F babel.cfg -o pqcli/locale/pqcli.pot \
    --project=pqcli --version=1.0.4 \
    --copyright-holder="pq-cli contributors" \
    --msgid-bugs-address="https://github.com/rr-/pq-cli/issues" .

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
`.po` を編集したら必ず手順3を再実行してください。

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

## 開発への参加

```sh
# リポジトリをクローン:
git clone https://github.com/rr-/pq-cli.git
cd pq-cli

# ローカルの venv に依存関係をインストール:
uv sync

# pre-commit フックをインストール:
uv run pre-commit install

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
