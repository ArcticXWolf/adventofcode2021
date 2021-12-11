from __future__ import annotations
import sys, os
import logging
from typing import Dict, Generator, List, Tuple
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
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]


class OctopusField:
    grid: Dict[Tuple[int, int], int]
    width: int
    height: int

    def __init__(self, input: List[str]) -> None:
        self.grid = {}
        self.width = 0
        self.height = 0
        for y, line in enumerate(input):
            for x, number in enumerate(list(line.strip())):
                self.grid[(x, y)] = int(number)
                self.height = max(self.height, y)
            self.width = max(self.width, x)
        self.width += 1
        self.height += 1

    def step(self) -> int:
        blacklist = {pos: False for pos in self.grid.keys()}
        count_flashes = 0

        self.increase_all()
        while self.are_any_octopus_flashing(blacklist):
            count_flashes += self.flash_once(blacklist)
        self.reset_octopus()

        return count_flashes

    def increase_all(self):
        for pos in self.grid.keys():
            self.grid[pos] += 1

    def reset_octopus(self):
        for pos in [pos for pos, x in self.grid.items() if x > 9]:
            self.grid[pos] = 0

    def positions_flashing(
        self, blacklist: List[Tuple[int, int], bool]
    ) -> List[Tuple[int, int]]:
        return [pos for pos, x in self.grid.items() if not blacklist[pos] and x > 9]

    def are_any_octopus_flashing(self, blacklist: List[Tuple[int, int], bool]):
        return len(self.positions_flashing(blacklist)) > 0

    def flash_once(self, blacklist: List[Tuple[int, int], bool]) -> int:
        pos_flashing = self.positions_flashing(blacklist)
        for pos in pos_flashing:
            blacklist[pos] = True
            for d in DIRECTIONS:
                if 0 <= pos[0] + d[0] < self.width and 0 <= pos[1] + d[1] < self.height:
                    self.grid[(pos[0] + d[0], pos[1] + d[1])] += 1
        return len(pos_flashing)

    def have_octopus_flashed_synchronized(self) -> bool:
        return all(x == 0 for _, x in self.grid.items())

    def __str__(self) -> str:
        text = ""
        for y in range(self.height):
            for x in range(self.width):
                color = ""
                if self.grid[(x, y)] == 0:
                    color = COLORS_RED
                text = f"{text}{color}{self.grid[(x,y)]}{COLOR_RESET}"
            text = f"{text}\n"
        return text


def main():
    with open(filename, "r") as f:
        field = OctopusField(f.readlines())
        flashes = 0
        logging.debug(f"Field at 0 ({flashes} flashes):\n{field}")
        x = 0
        while not field.have_octopus_flashed_synchronized():
            x += 1
            flashes += field.step()
            if x % 10 == 0:
                logging.debug(f"Field at {x} ({flashes} flashes):\n{field}")
            if x == 100:
                logging.info(f"Field at {x} ({flashes} flashes):\n{field}")

        logging.info(f"Field at {x} ({flashes} flashes, SYNCHRONIZED):\n{field}")


main()