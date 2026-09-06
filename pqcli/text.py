import typing as T
from dataclasses import dataclass

from pqcli.i18n import _

Renderable = T.Union["Phrase", str, int]


class Phrase:
    """User-visible text that is translated when rendered, not when built.

    The game composes a lot of text (quest captions, task sentences, item
    names) and then pickles it into the save file. Storing the finished
    sentence freezes it in whatever language was active at the time and bakes
    English word order into the data. Storing the msgid plus its parameters
    instead keeps the text re-renderable, so a language change reaches
    existing saves and translators can reorder the parts in the catalog.
    """

    def render(self) -> str:
        raise NotImplementedError("not implemented")


@dataclass(frozen=True)
class Raw(Phrase):
    """Text that is already final: proper names, numbers, legacy saves."""

    text: str

    def render(self) -> str:
        return self.text


@dataclass(frozen=True)
class Term(Phrase):
    """A single word or name from the game-data tables in pqcli.config."""

    msgid: str

    def render(self) -> str:
        return _(self.msgid)


@dataclass(frozen=True)
class Template(Phrase):
    """A sentence with holes, filled by other phrases.

    ``params`` is a tuple of pairs, not a dict, so the phrase compares by
    value -- the inventory merges item stacks by equality.
    """

    msgid: str
    params: T.Tuple[T.Tuple[str, Phrase], ...] = ()

    def render(self) -> str:
        return _(self.msgid).format(
            **{name: value.render() for name, value in self.params}
        )


@dataclass(frozen=True)
class Lower(Phrase):
    """Render the inner phrase in lower case, for backends that want it."""

    inner: Phrase

    def render(self) -> str:
        return self.inner.render().lower()


def as_phrase(value: Renderable) -> Phrase:
    if isinstance(value, Phrase):
        return value
    return Raw(str(value))


def phrase(msgid: str, **params: Renderable) -> Phrase:
    """Build a deferred ``_(msgid).format(**params)``."""
    if not params:
        return Term(msgid)
    return Template(
        msgid, tuple((name, as_phrase(v)) for name, v in params.items())
    )
