import curses
import typing as T

from pqcli.ui.curses.util import display_width, truncate_to_width
from pqcli.ui.curses.widgets import (
    DataTable,
    Focusable,
    ListBox,
    ProgressBar,
    WindowWrapper,
)


class ProgressBarWindow(WindowWrapper):
    def __init__(
        self,
        parent: T.Any,
        h: int,
        w: int,
        y: int,
        x: int,
        title: str,
        show_time: bool,
    ) -> None:
        super().__init__(parent, h, w, y, x)

        self._title = title
        self._cur_pos = 0.0
        self._max_pos = 1.0
        self._progress_title = ""

        try:
            self._progress_bar_win = (
                self._win.derwin(3, w, h - 3, 0) if self._win else None
            )
        except curses.error:
            self._progress_bar_win = None
        self._progress_bar = ProgressBar(
            self._progress_bar_win, 1, w - 2, 1, 1, show_time=show_time
        )

    def stop(self) -> None:
        super().stop()
        self._progress_bar.stop()

        del self._progress_bar_win
        self._progress_bar_win = None

    def _render_title(self) -> None:
        if not self._win:
            return
        title = truncate_to_width(self._title, self.getmaxyx()[1] - 1)
        x = max(0, (self.getmaxyx()[1] - display_width(title)) // 2)
        if title:
            self._win.addstr(0, x, title)

    def _render_progress_bar(self) -> None:
        if not self._progress_bar_win:
            return

        self._progress_bar_win.erase()

        with Focusable.focus_standout(self, self._progress_bar_win):
            self._progress_bar_win.border(
                curses.ACS_VLINE,
                curses.ACS_VLINE,
                curses.ACS_HLINE,
                curses.ACS_HLINE,
                curses.ACS_LTEE,
                curses.ACS_RTEE,
                curses.ACS_LLCORNER,
                curses.ACS_LRCORNER,
            )

            text = truncate_to_width(
                self._progress_title,
                self._progress_bar_win.getmaxyx()[1] - 1,
            )
            x = max(0, (self.getmaxyx()[1] - display_width(text)) // 2)
            if text:
                self._progress_bar_win.addstr(0, x, text)
        self._progress_bar.set_position(self._cur_pos, self._max_pos)
        self._progress_bar_win.noutrefresh()


class DataTableProgressBarWindow(ProgressBarWindow):
    def __init__(
        self,
        parent: T.Any,
        h: int,
        w: int,
        y: int,
        x: int,
        title: str,
        align_right: bool,
        show_time: bool,
    ) -> None:
        super().__init__(parent, h, w, y, x, title, show_time)

        self._data_table = DataTable(
            self._win, h - 4, w - 2, 1, 1, align_right
        )

    def stop(self) -> None:
        super().stop()
        self._data_table.stop()

    def _render_data_table(self) -> None:
        if not self._win:
            return

        with Focusable.focus_standout(self, self._win):
            self._win.box()
            self._render_title()

        self._win.noutrefresh()
        self._data_table.render()

    def _render(self) -> None:
        self._render_data_table()
        self._render_progress_bar()


class ListBoxProgressBarWindow(ProgressBarWindow):
    def __init__(
        self,
        parent: T.Any,
        h: int,
        w: int,
        y: int,
        x: int,
        title: str,
        show_time: bool,
    ) -> None:
        super().__init__(parent, h, w, y, x, title, show_time)

        self._list_box = ListBox(self._win, h - 4, w - 2, 1, 1)

    def stop(self) -> None:
        super().stop()
        self._list_box.stop()

    def _render_list_box(self) -> None:
        if not self._win:
            return

        with Focusable.focus_standout(self, self._win):
            self._win.box()
            self._render_title()

        self._win.noutrefresh()
        self._list_box.render()

    def _render(self) -> None:
        self._render_list_box()
        self._render_progress_bar()
