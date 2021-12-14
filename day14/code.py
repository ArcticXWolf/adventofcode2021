from __future__ import annotations
import sys, os, copy
import logging
from typing import Dict, Generator, List, Set, Tuple

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


def parse_input(
    input: List[str],
) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, str]]:
    character_counts: Dict[str, int] = {}
    pair_counts: Dict[str, int] = {}
    rules: Dict[str, str] = {}

    template = ""
    for line in [l.strip() for l in input]:
        if line == "":
            continue
        if "->" in line:
            pair, result = line.split("->")
            rules[pair.strip()] = result.strip()
            pair_counts[pair.strip()] = 0
            character_counts[pair.strip()[0]] = 0
            character_counts[pair.strip()[1]] = 0
            character_counts[result.strip()] = 0
            continue
        template = line

    for i in range(len(template)):
        character_counts[template[i]] += 1
        if i + 1 < len(template):
            pair_counts[f"{template[i]}{template[i+1]}"] += 1

    return character_counts, pair_counts, rules


def step(
    character_counts: Dict[str, int], pair_counts: Dict[str, int], rules: Dict[str, str]
) -> Tuple[Dict[str, int], Dict[str, int]]:
    new_pair_counts = copy.deepcopy(pair_counts)
    new_character_counts = copy.deepcopy(character_counts)

    for pair, count in pair_counts.items():
        if count == 0:
            continue
        new_pair_counts[pair] -= count
        new_pair1, new_pair2 = f"{pair[0]}{rules[pair]}", f"{rules[pair]}{pair[1]}"
        new_pair_counts[new_pair1] += count
        new_pair_counts[new_pair2] += count
        new_character_counts[rules[pair]] += count

    return new_character_counts, new_pair_counts


def main():
    with open(filename, "r") as f:
        cc, pc, r = parse_input(f.readlines())
        logging.debug("CC %s", cc)
        logging.debug("PC %s", pc)
        logging.debug("R %s", r)

        for i in range(40):
            cc, pc = step(cc, pc, r)
            logging.info("--- STEP %d ---", i + 1)
            logging.debug("CC %s", cc)
            logging.debug("PC %s", pc)
            logging.info(
                "Length %d, Most %s %d, Least %s %d, Diff %d",
                sum(x for x in cc.values()),
                max(cc, key=cc.get),
                max(cc.values()),
                min(cc, key=cc.get),
                min(cc.values()),
                max(cc.values()) - min(cc.values()),
            )


main()