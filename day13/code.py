from __future__ import annotations
import sys, os
import logging
from typing import Dict, Generator, List, Set, Tuple
from collections import Counter
import statistics, math

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


def get_grid_str(grid: Set[Tuple[int, int]]) -> str:
    width = max([x for x, _ in grid]) + 1
    height = max([y for _, y in grid]) + 1

    text = ""
    for y in range(height):
        for x in range(width):
            if (x, y) in grid:
                text = f"{text}#"
                continue
            text = f"{text}."
        text = f"{text}\n"

    return text


def fold(
    points: Set[Tuple[int, int]], axis: str, distance: int
) -> Set[Tuple[int, int]]:
    new_points = set()

    for x, y in points:
        new_x, new_y = x, y

        if axis == "x" and x > distance:
            new_x = distance - abs(x - distance)

        if axis == "y" and y > distance:
            new_y = distance - abs(y - distance)

        new_points.add((new_x, new_y))

    return new_points


def main():
    with open(filename, "r") as f:
        points = set()
        actions = []

        for line in [l.strip() for l in f.readlines()]:
            if line == "":
                continue
            if line.startswith("fold along "):
                axis, distance = line[11:].split("=")
                actions.append((axis, int(distance)))
                continue
            x, y = line.split(",")
            points.add((int(x), int(y)))

        logging.info(f"Initial points: {len(points)}")
        # logging.debug("%s", get_grid_str(points))

        for axis, distance in actions:
            points = fold(points, axis, distance)
            logging.info(f"After fold along {axis}={distance}: {len(points)}")
        logging.info("%s", get_grid_str(points))


main()