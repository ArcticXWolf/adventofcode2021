from __future__ import annotations
import sys, os, re
import logging
from typing import Deque, Dict, Generator, List, Set, Tuple, Union

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"
LINE_REGEX = re.compile("target area: x=(-?\d+)\.\.(-?\d+), y=(-?\d+)\.\.(-?\d+)")

# Shhh! Yeah, it is brute-force.. But I had little time for this task :D


def would_hit_by_y(
    current: Tuple[int, int],
    start: Tuple[int, int],
    stop: Tuple[int, int],
    velocity: Tuple[int, int],
) -> Tuple[bool, int]:
    if current[1] < start[1]:
        return False, current[1]
    if start[1] <= current[1] <= stop[1]:
        return True, current[1]

    new_max_y = 0
    while current[1] >= start[1]:
        new_max_y = max(new_max_y, current[1])
        current = (current[0], current[1] + velocity[1])
        velocity = (velocity[0], velocity[1] - 1)
        if start[1] <= current[1] <= stop[1]:
            return True, new_max_y

    return False, new_max_y


def would_both_hit(
    current: Tuple[int, int],
    start: Tuple[int, int],
    stop: Tuple[int, int],
    velocity: Tuple[int, int],
) -> Tuple[bool, int]:
    if current[1] < start[1] or current[0] > stop[0]:
        return False, current[1]
    if start[1] <= current[1] <= stop[1] and start[0] <= current[0] <= stop[0]:
        return True, current[1]

    new_max_y = 0
    while current[1] >= start[1] and current[0] <= stop[0]:
        new_max_y = max(new_max_y, current[1])
        current = (current[0] + velocity[0], current[1] + velocity[1])
        new_x_vel = 0
        if velocity[0] > 0:
            new_x_vel = velocity[0] - 1
        if velocity[0] < 0:
            new_x_vel = velocity[0] + 1
        velocity = (new_x_vel, velocity[1] - 1)
        if start[1] <= current[1] <= stop[1] and start[0] <= current[0] <= stop[0]:
            return True, new_max_y

    return False, new_max_y


def main():
    with open(filename, "r") as f:
        matches = LINE_REGEX.match(f.readline().strip())
        if matches == None:
            raise Exception("line input malformed")
        start, stop = (int(matches.group(1)), int(matches.group(3))), (
            int(matches.group(2)),
            int(matches.group(4)),
        )
        logging.debug("Parsed range: %s to %s", start, stop)

        possible_y_vel = [
            (y, would_hit_by_y((0, 0), start, stop, (0, y)))
            for y in range(-1000, 10000)
        ]
        possible_combinations = []
        result_y_max = 0
        for y, result in possible_y_vel:
            if not result[0]:
                continue
            for x in range(0, 10000):
                would_hit, y_max = would_both_hit((0, 0), start, stop, (x, y))
                if would_hit:
                    possible_combinations.append((x, y, y_max))
                    result_y_max = max(result_y_max, y_max)
        logging.debug("Possible y values: %s", possible_y_vel)
        logging.debug(
            "Possible vels(%d): %s", len(possible_combinations), possible_combinations
        )
        logging.info("Max y: %s", result_y_max)
        logging.info("Number of combinations: %s", len(possible_combinations))


main()