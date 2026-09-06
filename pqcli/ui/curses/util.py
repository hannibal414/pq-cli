import curses
import curses.ascii
import typing as T
from dataclasses import dataclass

from wcwidth import wcswidth

KEYS_CYCLE = {curses.ascii.TAB}
KEYS_DOWN = set(map(ord, "jJ")) | {curses.KEY_DOWN}
KEYS_LEFT = set(map(ord, "hH")) | {curses.KEY_LEFT}
KEYS_RIGHT = set(map(ord, "lL")) | {curses.KEY_RIGHT}
KEYS_UP = set(map(ord, "kK")) | {curses.KEY_UP}
KEYS_CANCEL = set(map(ord, "qQ")) | {curses.ascii.ESC}


@dataclass
class Choice:
    keys: T.List[int]
    desc: str
    callback: T.Callable[..., T.Any]


def first(source: T.Iterable[T.Any], default: T.Any = None) -> T.Any:
    return next(iter(source), default)


def display_width(text: str) -> int:
    """Terminal columns occupied by text.

    CJK glyphs take two columns, so len() would undercount them and throw off
    both centering and truncation. wcswidth returns -1 for unprintable input;
    fall back to len() there.
    """
    width = wcswidth(text)
    return len(text) if width < 0 else width


def truncate_to_width(text: str, max_width: int) -> str:
    """Clip text so it renders in at most max_width columns."""
    if max_width <= 0:
        return ""
    if display_width(text) <= max_width:
        return text
    result: T.List[str] = []
    width = 0
    for char in text:
        char_width = display_width(char)
        if width + char_width > max_width:
            break
        result.append(char)
        width += char_width
    return "".join(result)


def pad_to_width(text: str, width: int) -> str:
    """Left-align text into width columns (a display-width aware ljust)."""
    return text + " " * max(0, width - display_width(text))
