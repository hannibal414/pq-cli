import typing as T

from pqcli.i18n import _
from pqcli.lingo import to_roman
from pqcli.mechanic import Player, Spell
from pqcli.ui.curses.util import display_width, truncate_to_width
from pqcli.ui.curses.widgets import DataTable, Focusable, WindowWrapper


class SpellBookWindow(Focusable, WindowWrapper):
    def __init__(
        self, player: Player, parent: T.Any, h: int, w: int, y: int, x: int
    ) -> None:
        super().__init__(parent, h, w, y, x)
        self._on_focus_change += self._render

        self._data_table = DataTable(
            self._win, h - 2, w - 2, 1, 1, align_right=True
        )

        self._player = player
        self._player.spell_book.connect("add", self._sync_spell_add)
        self._player.spell_book.connect("change", self._sync_spell_change)

        self.sync()

    def stop(self) -> None:
        super().stop()
        self._data_table.stop()

        self._player.spell_book.disconnect("add", self._sync_spell_add)
        self._player.spell_book.disconnect("change", self._sync_spell_change)

    def scroll_page_up(self) -> None:
        self._data_table.scroll_page_up()
        self._render()

    def scroll_page_down(self) -> None:
        self._data_table.scroll_page_down()
        self._render()

    def sync(self) -> None:
        self._data_table.clear()
        for spell in self._player.spell_book:
            self._data_table.add(_(spell.name), to_roman(spell.level))
        self._data_table.select(None)
        self._render()

    def _sync_spell_add(self, spell: Spell) -> None:
        self._data_table.add(_(spell.name), to_roman(spell.level))
        self._data_table.select(_(spell.name))
        self._render()

    def _sync_spell_change(self, spell: Spell) -> None:
        self._data_table.set(_(spell.name), to_roman(spell.level))
        self._data_table.select(_(spell.name))
        self._render()

    def _render(self) -> None:
        if not self._win:
            return

        with self.focus_standout(self._win):
            self._win.box()
            text = truncate_to_width(_(" Spell Book "), self.getmaxyx()[1])
            x = max(0, (self.getmaxyx()[1] - display_width(text)) // 2)
            if text:
                self._win.addstr(0, x, text)

        self._win.noutrefresh()
        self._data_table.render()
