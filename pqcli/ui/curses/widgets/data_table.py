import curses
import typing as T

from pqcli.ui.curses.colors import COLOR_HIGHLIGHT, has_colors
from pqcli.ui.curses.util import display_width, truncate_to_width

from .scrollable import Scrollable


class DataTable(Scrollable):
    def __init__(
        self,
        parent: T.Any,
        h: int,
        w: int,
        y: int,
        x: int,
        align_right: bool = False,
    ) -> None:
        super().__init__(parent, h, w, y, x)

        self._align_right = align_right
        self._items: T.List[T.Tuple[str, str]]
        self._selected: T.Optional[int] = None

    def add(self, text: str, value: str) -> None:
        self._items.append((text, value))
        self.scroll_to_item(-1)

    def set(self, text: str, value: str) -> None:
        idx = self.get_idx(text)
        if idx is None:
            self.add(text, value)
        else:
            self._items[idx] = (self._items[idx][0], value)
            self.scroll_to_item(idx)

    def delete(self, text: str) -> None:
        idx = self.get_idx(text)
        if idx is not None:
            del self._items[idx]
            self.scroll_to_item(idx)

    def select(self, text: T.Optional[str]) -> None:
        self._selected = None if text is None else self.get_idx(text)

    def get_idx(self, text: str) -> T.Optional[int]:
        for idx, row in enumerate(self._items):
            if row[0].strip() == text.strip():
                return idx
        return None

    def _render_impl(self, h: int, w: int) -> None:
        assert self._pad
        if self._align_right:
            for y, row in enumerate(self._items):
                if y == self._selected and has_colors():
                    self._pad.attron(curses.color_pair(COLOR_HIGHLIGHT))
                self._pad.move(y, 0)
                key = truncate_to_width(row[0], w)
                if key:
                    self._pad.addstr(key)
                value = truncate_to_width(row[1], w)
                col2_x = max(0, w - display_width(value))
                if col2_x < w and value:
                    self._pad.move(y, col2_x)
                    self._pad.addstr(value)
                if y == self._selected and has_colors():
                    self._pad.attroff(curses.color_pair(COLOR_HIGHLIGHT))
        else:
            col2_x = self._get_col_width(0)
            for y, row in enumerate(self._items):
                if y == self._selected and has_colors():
                    self._pad.attron(curses.color_pair(COLOR_HIGHLIGHT))
                key = truncate_to_width(row[0], w)
                if key:
                    self._pad.addstr(y, 0, key)
                # Clip the value to the columns left after the key column
                value = truncate_to_width(row[1], w - col2_x)
                if col2_x < w and value:
                    self._pad.addstr(y, col2_x, value)
                if y == self._selected and has_colors():
                    self._pad.attroff(curses.color_pair(COLOR_HIGHLIGHT))

    def _get_col_width(self, x: int) -> int:
        return max([display_width(row[0]) for row in self._items] + [0])
