import curses
import typing as T

from pqcli.ui.curses.colors import COLOR_HIGHLIGHT, has_colors
from pqcli.ui.curses.util import truncate_to_width

from .scrollable import Scrollable

MARKER_DONE = "[X] "
MARKER_PENDING = "[ ] "


class ListBox(Scrollable):
    """A scrollable list whose entries carry a done/pending marker.

    The marker is owned by the widget rather than baked into the caller's
    text, so marking an entry done never has to slice the prefix back off --
    a slice that assumed a 4-column ASCII prefix and broke on wide glyphs.
    """

    _items: T.List[T.Tuple[str, bool]]

    def __init__(self, parent: T.Any, h: int, w: int, y: int, x: int) -> None:
        super().__init__(parent, h, w, y, x)
        self._selected: T.Optional[int] = None

    def add(self, text: str) -> None:
        self._items.append((text, False))
        self.scroll_to_item(-1)

    def mark_done(self, idx: int) -> None:
        if not self._items:
            return
        if idx < 0:
            idx %= len(self._items)
        self._items[idx] = (self._items[idx][0], True)

    def delete(self, idx: int, count: int = 1) -> None:
        del self._items[idx : idx + count]

    def select(self, idx: T.Optional[int]) -> None:
        if idx < 0 and len(self._items):
            idx %= len(self._items)
        self._selected = idx

    def _render_impl(self, h: int, w: int) -> None:
        assert self._pad
        for y, (text, done) in enumerate(self._items):
            if y == self._selected and has_colors():
                self._pad.attron(curses.color_pair(COLOR_HIGHLIGHT))
            item = truncate_to_width(
                (MARKER_DONE if done else MARKER_PENDING) + text, w
            )
            if item:
                self._pad.addstr(y, 0, item)
            if y == self._selected and has_colors():
                self._pad.attroff(curses.color_pair(COLOR_HIGHLIGHT))
