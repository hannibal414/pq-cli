import typing as T

from pqcli.i18n import _
from pqcli.mechanic import EquipmentType, Player
from pqcli.text import Phrase
from pqcli.ui.curses.util import display_width, pad_to_width, truncate_to_width
from pqcli.ui.curses.widgets import DataTable, Focusable, WindowWrapper


class EquipmentWindow(Focusable, WindowWrapper):
    def __init__(
        self, player: Player, parent: T.Any, h: int, w: int, y: int, x: int
    ) -> None:
        super().__init__(parent, h, w, y, x)
        self._on_focus_change += self._render

        self._data_table = DataTable(
            self._win, h - 2, w - 2, 1, 1, align_right=False
        )

        self._player = player
        self._player.equipment.connect("change", self._sync_equipment_change)

        self.sync()

    def stop(self) -> None:
        super().stop()
        self._data_table.stop()

        self._player.equipment.disconnect(
            "change", self._sync_equipment_change
        )

    def sync(self) -> None:
        self._data_table.clear()
        for equipment_type in EquipmentType:
            self._data_table.add(
                pad_to_width(_(equipment_type.value), 15),
                self._render_item(self._player.equipment[equipment_type]),
            )
        self._data_table.select(None)
        self._render()

    def _sync_equipment_change(
        self, equipment_type: EquipmentType, item_name: T.Optional[str]
    ) -> None:
        self._data_table.set(
            _(equipment_type.value), self._render_item(item_name)
        )
        self._data_table.select(_(equipment_type.value))
        self._render()

    @staticmethod
    def _render_item(item_name: T.Optional[Phrase]) -> str:
        return item_name.render() if item_name is not None else ""

    def _render(self) -> None:
        if not self._win:
            return

        with self.focus_standout(self._win):
            self._win.box()
            text = truncate_to_width(_(" Equipment "), self.getmaxyx()[1])
            x = max(0, (self.getmaxyx()[1] - display_width(text)) // 2)
            if text:
                self._win.addstr(0, x, text)

        self._win.noutrefresh()
        self._data_table.render()
