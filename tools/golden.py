"""Dump every user-visible string a seeded simulation produces.

The random number generator is seeded, so the output is fixed for a given
revision. Diffing it against ``golden_expected.txt`` says whether a change
altered what the game displays -- the safety net this repo otherwise lacks,
since there are no tests and no CI.

    uv run python tools/golden.py            # print the dump
    uv run python tools/golden.py --check    # diff it against the expected file
    uv run python tools/golden.py --update   # accept the current output

A diff is not automatically a bug: it is the list of display changes a commit
makes. Read it, and if it is intended, re-record with --update.

Coverage is what five seeds of low-level play reach: NPC opponents, the bound
"Battle-"/"Were-" prefixes and the separated adjectives all appear. The
"imaginary" and "messianic" branches need a level gap of ten or more and do
not, so they are not protected here.
"""

import argparse
import datetime
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pqcli import random  # noqa: E402
from pqcli.config import CLASSES, RACES  # noqa: E402
from pqcli.i18n import set_language  # noqa: E402
from pqcli.mechanic import Player, Simulation, StatsBuilder  # noqa: E402

EXPECTED = Path(__file__).with_name("golden_expected.txt")

# Several seeds, because one run only walks one path through the generators --
# NPC opponents, for instance, come up one time in twenty-five.
SEEDS = ["alpha", "bravo", "charlie", "delta", "echo"]
TICKS = 20000
OPENING_TASKS = 8


def show(value: object) -> str:
    render = getattr(value, "render", None)
    return render() if callable(render) else str(value)


def run(seed: str) -> list:
    random.seed(seed)
    player = Player(
        birthday=datetime.datetime(2020, 1, 1),
        name="Tester",
        race=RACES[3],
        class_=CLASSES[5],
        stats=StatsBuilder().roll(),
    )
    simulation = Simulation(player)

    opening: list = []
    every = set()
    for _tick in range(TICKS):
        simulation.tick(100.0)
        description = show(player.task.description)
        every.add(description)
        if len(opening) < OPENING_TASKS and (
            not opening or opening[-1] != description
        ):
            opening.append(description)

    lines = [f"=== seed {seed}"]
    # The opening runs in a fixed order, so it catches sequencing changes.
    lines.append("--- opening tasks")
    lines += [f"  {description}" for description in opening]
    # Everything else is recorded as a sorted set: order varies with how the
    # simulation interleaves, but the strings themselves must not.
    lines.append("--- all tasks")
    lines += [f"  {description}" for description in sorted(every)]

    lines.append("--- quests")
    lines += [f"  {show(quest)}" for quest in player.quest_book.quests]
    lines.append("--- inventory")
    lines += [
        f"  {show(item.name)} x{item.quantity} special={item.is_special}"
        for item in player.inventory
    ]
    lines.append("--- equipment")
    lines += [
        f"  {slot.value}: {show(name)}" for slot, name in player.equipment
    ]
    lines.append(f"--- best: {show(player.equipment.best)}")
    lines.append("--- spells")
    lines += [f"  {spell.name} {spell.level}" for spell in player.spell_book]
    lines.append(
        f"--- level={player.level} gold={player.inventory.gold} "
        f"act={player.quest_book.act}"
    )
    return lines


def dump() -> str:
    # Pin the language: the point is to catch changes to the English output,
    # not to notice that the developer's shell is set to something else.
    set_language("en")
    lines: list = []
    for seed in SEEDS:
        lines += run(seed)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        help="compare against the expected dump and exit non-zero on a diff",
    )
    group.add_argument(
        "--update",
        action="store_true",
        help="overwrite the expected dump with the current output",
    )
    args = parser.parse_args()

    current = dump()

    if args.update:
        EXPECTED.write_text(current)
        print(f"recorded {len(current.splitlines())} lines to {EXPECTED.name}")
        return 0

    if args.check:
        if not EXPECTED.exists():
            print(f"{EXPECTED} is missing; run with --update", file=sys.stderr)
            return 2
        expected = EXPECTED.read_text()
        if expected == current:
            print(f"golden output unchanged ({len(SEEDS)} seeds)")
            return 0
        sys.stdout.writelines(
            difflib.unified_diff(
                expected.splitlines(keepends=True),
                current.splitlines(keepends=True),
                fromfile="expected",
                tofile="current",
            )
        )
        return 1

    sys.stdout.write(current)
    return 0


if __name__ == "__main__":
    sys.exit(main())
