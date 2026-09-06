"""English grammar: articles, plurals and the adjective stack.

Everything here is a rule about *English*, so it is free to inspect English
text (spacing, capitalisation, suffixes). A backend for another language owns
its own rules and its own adjective tables; nothing outside this module should
assume any of it.
"""

import typing as T

from pqcli import random
from pqcli.i18n import N_
from pqcli.text import Lower, Phrase, Raw, Term, phrase

SICK_ADJECTIVES = [
    N_("dead"),
    N_("comatose"),
    N_("crippled"),
    N_("sick"),
    N_("undernourished"),
]

YOUNG_ADJECTIVES = [
    N_("foetal"),
    N_("baby"),
    N_("preadolescent"),
    N_("teenage"),
    N_("underage"),
]

BIG_ADJECTIVES = [
    N_("greater"),
    N_("massive"),
    N_("enormous"),
    N_("giant"),
    N_("titanic"),
]

SPECIAL_ADJECTIVES = [
    N_("veteran"),
    N_("cursed"),
    N_("warrior"),
    N_("undead"),
    N_("demon"),
]

SPECIAL_PREFIXES = [
    N_("Battle-"),
    N_("cursed "),
    N_("Were-"),
    N_("undead "),
    N_("demon "),
]

NAME_SYLLABLES = [
    "br|cr|dr|fr|gr|j|kr|l|m|n|pr||||r|sh|tr|v|wh|x|y|z".split("|"),
    "a|a|e|e|i|i|o|o|u|u|ae|ie|oo|ou".split("|"),
    "b|ck|d|g|k|m|n|p|t|v|x|z".split("|"),
]


def generate_name() -> Phrase:
    result = ""
    for i in range(6):
        result += random.choice(NAME_SYLLABLES[i % 3])
    return Raw(result.title())


def plural(subject: str) -> str:
    if subject.endswith("y"):
        return subject[:-1] + "ies"
    if subject.endswith("us"):
        return subject[:-2] + "i"
    if subject.endswith(("ch", "x", "s", "sh")):
        return subject + "es"
    if subject.endswith("f"):
        return subject[:-1] + "ves"
    if subject.endswith(("man", "Man")):
        return subject[:-2] + "en"
    return subject + "s"


def indefinite(subject: Phrase, qty: int) -> Phrase:
    if qty == 1:
        text = subject.render()
        msgid = (
            "an {subject}"
            if text.startswith(tuple("AEIOU?aeiou?"))
            else "a {subject}"
        )
        return phrase(msgid, subject=subject)
    return phrase(
        "{qty} {subject}",
        qty=qty,
        subject=Raw(plural(subject.render())),
    )


def definite(subject: Phrase, qty: int) -> Phrase:
    if qty > 1:
        subject = Raw(plural(subject.render()))
    return phrase("the {subject}", subject=subject)


def prefix(
    adjectives: T.List[str], m: int, subject: Phrase, spaced: bool = True
) -> Phrase:
    m = abs(m)
    if m < 1 or m > len(adjectives):
        return subject
    return phrase(
        "{adjective} {subject}" if spaced else "{adjective}{subject}",
        adjective=Term(adjectives[m - 1]),
        subject=subject,
    )


def sick(m: int, subject: Phrase) -> Phrase:
    return prefix(SICK_ADJECTIVES, 6 - abs(m), subject)


def young(m: int, subject: Phrase) -> Phrase:
    return prefix(YOUNG_ADJECTIVES, 6 - abs(m), subject)


def big(m: int, subject: Phrase) -> Phrase:
    return prefix(BIG_ADJECTIVES, m, subject)


def special(m: int, subject: Phrase) -> Phrase:
    # A multi-word name takes a separate adjective ("veteran Fire Ant"); a
    # single word takes a bound prefix ("Were-Ant"). Word boundaries are an
    # English notion, hence this lives in the English backend.
    if " " in subject.render():
        return prefix(SPECIAL_ADJECTIVES, m, subject)
    return prefix(SPECIAL_PREFIXES, m, subject, spaced=False)


def common_noun(subject: Phrase) -> Phrase:
    return Lower(subject)
