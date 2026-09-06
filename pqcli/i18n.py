import gettext
import os
import typing as T
from pathlib import Path

DOMAIN = "pqcli"
LOCALE_DIR = Path(__file__).parent / "locale"


def _languages() -> T.Optional[T.List[str]]:
    """Pick the language list to hand to gettext.

    ``PQCLI_LANG`` wins when set; otherwise ``None`` lets gettext consult the
    usual environment (``LANGUAGE``, ``LC_ALL``, ``LC_MESSAGES``, ``LANG``).
    """
    lang = os.environ.get("PQCLI_LANG", "").strip()
    if lang:
        return [lang]
    return None


def get_translation() -> gettext.NullTranslations:
    """Return the active catalog, falling back to the English msgids.

    ``fallback=True`` means a missing or unreadable ``.mo`` yields a
    ``NullTranslations``, whose ``gettext`` is the identity function -- so the
    game always renders in English rather than raising.
    """
    return gettext.translation(
        DOMAIN,
        localedir=LOCALE_DIR,
        languages=_languages(),
        fallback=True,
    )


_ = get_translation().gettext
