<p align="center">
  <img alt="Progress Quest" src="http://progressquest.com/pq.png">
</p>

*English | [日本語](README.ja.md)*

Relive the great adventure… this time in the terminal realm!

- Progress Quest site:  http://progressquest.com/
- Online version:       http://progressquest.com/play/
- Original version:     https://bitbucket.org/grumdrig/pq

## Features

- Faithful port of the game logic
- Saves (with backups) to `$XDG_CONFIG_HOME/pqcli/save.dat`
- Terminal interface that comes in 2 flavors:
    - Rich and colorful (`--curses`, default)
    - Minimal, suitable for raw grind (`--basic`)
- Ideal to run on your server

## How it looks like

Curses interface:

![Screenshot](screen-curses-logo.png)
![Screenshot](screen-curses.png)

Basic interface:

![Screenshot](screen-basic.png)

## How to install

If you have Python 3.10 or newer, just run `pip install --user pqcli` and you're
good to go! Then type `pqcli` to run the game.

In case if you want to use the git version, the process is just a bit more complex:

```console
$ git clone https://github.com/rr-/pq-cli.git
$ cd pq-cli
$ pip install --user .
```

## Docker / Docker Compose

The repository includes a `Dockerfile` and `docker-compose.yml` that run the
game with `--basic` and keep save data in a persistent named volume.

There is no registry pipeline required for this setup: build locally, then run
with Compose.

```console
# Build image locally from the Dockerfile
docker compose build

# First run (interactive): create your character in the shared save volume
docker compose run --rm pqcli-init

# Later runs on a server (detached, default save slot 1):
docker compose up -d pqcli

# List existing saves in the same volume:
docker compose run --rm pqcli-init pqcli --basic --list-saves

# Change detached slot if needed (example: slot 2):
PQCLI_SAVE_SLOT=2 docker compose up -d pqcli

# Follow logs / stop detached container:
docker compose logs -f pqcli
docker compose stop pqcli
```

On first run, if no save data exists in the mounted volume, `pqcli` will
automatically launch an interactive character-creation bootstrap in CLI mode
before starting the normal interface.

For server usage, run first-time setup without a forced slot (`pqcli-init`),
then run the long-lived detached service (`pqcli`) that loads slot `1` by
default.

## Languages

The game ships with English (the source language) and Japanese. Pick one with
the `PQCLI_LANG` environment variable:

```console
PQCLI_LANG=ja pqcli
PQCLI_LANG=en pqcli
```

When `PQCLI_LANG` is unset, the usual gettext environment is consulted
(`LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, `LANG`). If no catalog matches, the game
falls back to English.

Everything the game shows is translatable, including the game-data tables in
`pqcli/config.py` — monster, spell, race, class, item and equipment names. Those
English strings are *identities*, not display text: they are what the code, the
save files and the msgids all agree on, and the display layer resolves them
through the catalog at render time. Translating one therefore means adding a
msgstr, never editing `pqcli/config.py`.

Text is stored as a phrase (`pqcli/text.py`) — a msgid plus its parameters —
rather than as a finished sentence, so a language change reaches text that was
generated earlier, and translators can reorder the parts of a sentence in the
catalog. Text written by versions before phrases existed keeps the language it
was generated in, since the msgid it came from cannot be recovered.

English grammar (articles, plurals, the adjective stack) lives in
`pqcli/lingo/en.py`. `pqcli/lingo/__init__.py` picks a backend from the active
catalog and falls back to English, so adding `pqcli/lingo/<lang>.py` is how a
language gets its own rules.

### Working on translations

Translation tooling needs the dev dependencies (`uv sync`).

```console
# 1. Re-extract msgids from the source into the .pot template
uv run pybabel extract -F babel.cfg -k N_ -k Term -k phrase \
    -o pqcli/locale/pqcli.pot \
    --project=pqcli --version=1.0.4 \
    --copyright-holder="pq-cli contributors" \
    --msgid-bugs-address="https://github.com/rr-/pq-cli/issues" .

# 2. Merge the template into the existing catalogs
uv run pybabel update -i pqcli/locale/pqcli.pot -d pqcli/locale -D pqcli

# 3. Edit pqcli/locale/<lang>/LC_MESSAGES/pqcli.po, then compile to .mo
uv run pybabel compile -d pqcli/locale -D pqcli --statistics
```

To start a new language (`de` shown here):

```console
uv run pybabel init -i pqcli/locale/pqcli.pot -d pqcli/locale -l de -D pqcli
```

The compiled `.mo` files are what the game loads at runtime, so re-run step 3
after editing any `.po`. The `compile-catalogs` pre-commit hook does this for
you and fails the commit if the `.mo` was stale.

`-k N_ -k Term -k phrase` is what pulls the game data in: `N_()` marks a string
in `pqcli/config.py` for extraction without translating it there, `Term()` names
one of those strings at the point of use, and `phrase()` builds a deferred
sentence. When adding translatable strings to the source, wrap
them with `_()` from `pqcli.i18n` and prefer a single `.format()` template over
concatenation, so translators can reorder the parts:

```python
# good -- one msgid, placeholders can move
_("Selling {item}").format(item=indefinite(item.name, item.quantity))

# bad -- word order is baked into the code
_("Selling ") + indefinite(item.name, item.quantity)
```

Beware that `_` is the gettext function: never use it as a throwaway variable
name (`for _ in range(...)`) in a module that imports it.

### Checking the display did not change

There are no tests, so `tools/golden.py` stands in for one: it runs five seeded
simulations and dumps every string they display. `--check` diffs that against
`tools/golden_expected.txt` and fails on any difference; `--update` re-records
it once you have read the diff and want it. The `golden-output` pre-commit hook
runs the check for you. Translating does not change the English dump, so the
hook stays quiet during translation work and speaks up when code does.

## Contributing

```sh
# Clone the repository:
git clone https://github.com/rr-/pq-cli.git
cd pq-cli

# Install dependencies into a local venv:
uv sync

# Install pre-commit hooks:
uv run pre-commit install

# Run commands inside the venv:
uv run pqcli
```

This project uses [uv](https://docs.astral.sh/uv/) for packaging.
Install instructions are available at [uv installation](https://docs.astral.sh/uv/getting-started/installation/).

## Troubleshooting

### `_curses.error: init_pair() returned ERR`

If running on Linux and you get the error `_curses.error: init_pair() returned ERR`,
try making sure that your `$TERM` variable is set to a value which supports
256 colors, such as via the following:

    TERM=xterm-256color pqcli

