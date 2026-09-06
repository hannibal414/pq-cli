"""Language-dependent text helpers, dispatched to a per-language backend.

The public names here keep working regardless of the active catalog: a
language without its own backend falls back to English, which is what the
game did before backends existed.
"""

import datetime
import typing as T

from pqcli import random
from pqcli.i18n import _, current_language
from pqcli.text import Phrase, Raw, phrase

from . import en

_BACKENDS: T.Dict[str, T.Any] = {"en": en}


def _rule(name: str) -> T.Any:
    """Look up one rule, falling back to English per function.

    A new backend can therefore define only the rules its language actually
    differs on and inherit the rest, instead of having to reimplement all of
    them before it works at all.
    """
    backend = _BACKENDS.get(current_language())
    return getattr(backend, name, None) or getattr(en, name)


# -- language-neutral --------------------------------------------------------


def format_float(num: float) -> str:
    ret = f"{num:.01f}"
    if ret.endswith("0"):
        ret = ret[:-2]
    return ret


def format_timespan(timespan: datetime.timedelta) -> str:
    num = timespan.total_seconds()
    if num < 60.0:
        return _("~{num}s").format(num=int(num))
    num /= 60
    if num < 60.0:
        return _("~{num}m").format(num=int(num))
    num /= 60
    if num < 24.0:
        return _("~{num}h").format(num=format_float(num))
    num /= 24
    return _("~{num}d").format(num=format_float(num))


def to_roman(num: int) -> str:
    if not num:
        return "N"

    ret = ""

    def _rome(dn: int, ds: str) -> bool:
        nonlocal num, ret
        if num >= dn:
            num -= dn
            ret += ds
            return True
        return False

    if num < 0:
        ret = "-"
        num = -num

    while _rome(1000, "M"):
        pass
    _rome(900, "CM")
    _rome(500, "D")
    _rome(400, "CD")
    while _rome(100, "C"):
        pass
    _rome(90, "XC")
    _rome(50, "L")
    _rome(40, "XL")
    while _rome(10, "X"):
        pass
    _rome(9, "IX")
    _rome(5, "V")
    _rome(4, "IV")
    while _rome(1, "I"):
        pass
    return ret


def act_name(act: int) -> Phrase:
    if act == 0:
        return phrase("Prologue")
    return phrase("Act {numeral}", numeral=Raw(to_roman(act)))


def terminate_message(player_name: str) -> str:
    adjective = random.choice(
        [_("faithful"), _("noble"), _("loyal"), _("brave")]
    )
    return _("Terminate {adjective} {name}?").format(
        adjective=adjective, name=player_name
    )


# -- dispatched to the active language's backend -----------------------------


def generate_name() -> Phrase:
    return _rule("generate_name")()


def indefinite(subject: Phrase, qty: int) -> Phrase:
    return _rule("indefinite")(subject, qty)


def definite(subject: Phrase, qty: int) -> Phrase:
    return _rule("definite")(subject, qty)


def sick(m: int, subject: Phrase) -> Phrase:
    return _rule("sick")(m, subject)


def young(m: int, subject: Phrase) -> Phrase:
    return _rule("young")(m, subject)


def big(m: int, subject: Phrase) -> Phrase:
    return _rule("big")(m, subject)


def special(m: int, subject: Phrase) -> Phrase:
    return _rule("special")(m, subject)


def common_noun(subject: Phrase) -> Phrase:
    return _rule("common_noun")(subject)
