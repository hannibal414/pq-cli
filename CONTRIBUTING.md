# Contributing

*English | [日本語](CONTRIBUTING.ja.md)*

Two kinds of contribution need very different setups, so pick the one you are
here for.

## Translating

You need a `.po` editor and nothing else — no Python, no build tools.
[Poedit](https://poedit.net/) is free and runs on Windows, macOS and Linux;
any text editor works too.

1. Open `pqcli/locale/<language>/LC_MESSAGES/pqcli.po` — for Japanese that is
   `pqcli/locale/ja/LC_MESSAGES/pqcli.po`.
2. Fill in the `msgstr` lines you want to translate.
3. Open a pull request containing only that `.po` file.

That is the whole process. You do **not** need to compile anything: `.mo`
files are build output, are not in git, and are generated when a release is
built.

Partial work is welcome. Anything left untranslated falls back to English, so
translating ten entries and stopping leaves the game perfectly playable. As of
writing, Japanese covers 207 of 982 messages.

### What the strings are

Roughly a hundred are interface text and sentence frames. The rest are game
data — monster, spell, race, class, item and equipment names — and those are
where the work is, because Progress Quest is a parody: `Cone of Annoyance`,
`Slime Finger`, `Battle-Ghoul`. Keeping a joke funny in another language is
rewriting, not lookup. Prefer a name that lands over one that is literal, and
keep a given name identical everywhere it appears.

A sentence frame looks like `Executing {monster}`. Keep the `{...}` markers,
but move them wherever your language needs them — that is exactly why they are
markers instead of glued-together words.

### Do not edit `pqcli/config.py`

The English strings in that file are identities, not display text: the code,
the save files and the msgids all agree on them. Changing one there breaks the
link to every catalog. Translate by adding a `msgstr`, always.

### Starting a new language

```console
uv run pybabel init -i pqcli/locale/pqcli.pot -d pqcli/locale -l de -D pqcli
```

Some languages also need grammar the catalog cannot express — articles,
plurals, counters, adjective placement. Those live in `pqcli/lingo/<lang>.py`,
registered in `_BACKENDS` in `pqcli/lingo/__init__.py`. Define only the rules
your language actually differs on; everything else falls back to English, so a
two-function backend is a perfectly good start.

## Changing the code

```console
git clone https://github.com/hannibal414/pq-cli.git
cd pq-cli
uv sync
uv run pre-commit install

# Once, so the game can run in a language other than English:
uv run pybabel compile -d pqcli/locale -D pqcli

uv run pqcli
```

There is no test suite. `tools/golden.py` stands in for one: it runs five
seeded simulations and dumps every string they display, and the
`golden-output` pre-commit hook diffs that against `tools/golden_expected.txt`.

A diff there is not automatically a bug — it is the list of display changes
your commit makes. Read it. If it is what you intended, record it:

```console
uv run python tools/golden.py --update
```

Translation work never changes that dump, so the hook stays quiet while you
are editing catalogs.

### Adding a string to the source

Wrap it with `_()` from `pqcli.i18n`, and keep a whole sentence in one msgid
with named placeholders rather than concatenating pieces:

```python
# good -- one msgid, the translator can reorder it
_("Selling {item}").format(item=name)

# bad -- English word order is now baked into the code
_("Selling ") + name
```

Text that gets stored in a save file should be a phrase from `pqcli.text`
rather than a rendered string, so it can be re-rendered after a language
change. `_` is the gettext function: never use it as a throwaway variable in a
module that imports it.

## Upstream

This is a fork of [rr-/pq-cli](https://github.com/rr-/pq-cli). Changes that are
not about localization are often better sent there.
