from pqcli.ui.curses.util import truncate_to_width

from .base import WindowWrapper


class Label(WindowWrapper):
    def set_text(self, text: str) -> None:
        if not self._win:
            return
        self._win.erase()
        text = truncate_to_width(text, self.getmaxyx()[1] - 1)
        if text:
            self._win.addstr(text)
        self._win.noutrefresh()
