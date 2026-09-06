import gettext
import os
import typing as T
from pathlib import Path

DOMAIN = "pqcli"
LOCALE_DIR = Path(__file__).parent / "locale"


def _languages(lang: T.Optional[str] = None) -> T.Optional[T.List[str]]:
    """Pick the language list to hand to gettext.

    An explicit ``lang`` wins, then ``PQCLI_LANG``; otherwise ``None`` lets
    gettext consult the usual environment (``LANGUAGE``, ``LC_ALL``,
    ``LC_MESSAGES``, ``LANG``).
    """
    if lang:
        return [lang]
    env_lang = os.environ.get("PQCLI_LANG", "").strip()
    if env_lang:
        return [env_lang]
    return None


def get_translation(
    lang: T.Optional[str] = None,
) -> gettext.NullTranslations:
    """Return a catalog; a missing .mo falls back to the English msgids."""
    return gettext.translation(
        DOMAIN,
        localedir=LOCALE_DIR,
        languages=_languages(lang),
        fallback=True,
    )


_current: gettext.NullTranslations = get_translation()


def set_language(lang: T.Optional[str]) -> None:
    """Rebind the active catalog.

    Lookup happens per call, so this reaches text composed earlier and only
    rendered now.
    """
    global _current
    _current = get_translation(lang)


def current_language() -> str:
    """The active language as a bare code, read back from the catalog."""
    language = (_current.info() or {}).get("language", "")
    return language.split("_")[0].strip().lower() or "en"


def _(message: str) -> str:
    return _current.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Plural-aware lookup; each catalog declares its own Plural-Forms."""
    return _current.ngettext(singular, plural, n)


def N_(message: str) -> str:
    """Mark a string for extraction without translating it here.

    Used for the game-data tables in ``pqcli.config``, whose English strings
    stay the identity that code, save files and msgids agree on.
    """
    return message
