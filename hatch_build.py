"""Compile the gettext catalogs when building a distribution.

The .mo files are build output rather than source: they are generated from the
.po files and kept out of git, so a translation pull request carries only the
text someone actually edited and never a stale recompiled binary.
"""

from pathlib import Path
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        from babel.messages.mofile import write_mo
        from babel.messages.pofile import read_po

        locale_dir = Path(self.root) / "pqcli" / "locale"
        for po_path in sorted(locale_dir.glob("*/LC_MESSAGES/*.po")):
            with po_path.open("rb") as handle:
                catalog = read_po(handle, locale=po_path.parts[-3])
            with po_path.with_suffix(".mo").open("wb") as handle:
                write_mo(handle, catalog)
