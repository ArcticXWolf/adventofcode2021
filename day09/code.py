from __future__ import annotations
import sys, os
import logging
from typing import Dict, Generator, List, Tuple

logging.basicConfig(format="%(message)s", level=logging.DEBUG)
COLORS = [f"\x1b[38;5;{d}m" for d in range(124, 232)]
COLORS[0] = "\x1b[38;5;8m"
COLOR_RESET = "\x1b[0m"

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class LavaCave:
    heightmap: List[List[int]]
    coloring: List[List[int]]

    def __init__(self, lines: str) -> None:
        self.heightmap = []

        for line in lines:
            current_row = []
            for height in list(line.strip()):
                current_row.append(int(height))
            self.heightmap.append(current_row)
        self.create_coloring()

    def xheight(self) -> int:
        return len(self.heightmap[0])

    def yheight(self) -> int:
        return len(self.heightmap)

    def get_low_points(self) -> Generator[Tuple[int, int, int]]:
        for x in range(self.xheight()):
            for y in range(self.yheight()):
                current_height = self.heightmap[y][x]
                neighbor_heights = [
                    self.heightmap[y + y_offset][x + x_offset]
                    for x_offset, y_offset in DIRECTIONS
                    if 0 <= y + y_offset < self.yheight()
                    and 0 <= x + x_offset < self.xheight()
                ]

                if current_height < min(neighbor_heights):
                    yield x, y, current_height

    def get_riskfactor(self) -> int:
        return sum([h + 1 for _, _, h in self.get_low_points()])

    def create_coloring(self) -> None:
        self.coloring = [[0] * len(x) for x in self.heightmap]
        color = 1
        for low_x, low_y, _ in self.get_low_points():
            queue = [(low_x, low_y)]
            while len(queue) > 0:
                x, y = queue.pop(0)
                self.coloring[y][x] = color
                for dx, dy in DIRECTIONS:
                    if (
                        0 <= x + dx < self.xheight()
                        and 0 <= y + dy < self.yheight()
                        and self.heightmap[y + dy][x + dx] < 9
                        and self.coloring[y + dy][x + dx] <= 0
                    ):
                        queue.append((x + dx, y + dy))

            color += 1

    def get_basin_sizes(self) -> Generator[int]:
        for low_x, low_y, _ in self.get_low_points():
            color = self.coloring[low_y][low_x]
            yield sum(
                [
                    self.coloring[y][x] == color
                    for y in range(self.yheight())
                    for x in range(self.xheight())
                ]
            )

    def get_riskfactor_by_basins(self) -> int:
        basin_sizes = sorted(list(self.get_basin_sizes()))
        return basin_sizes.pop() * basin_sizes.pop() * basin_sizes.pop()

    def __str__(self) -> str:
        text = ""
        for y in range(self.yheight()):
            for x in range(self.xheight()):
                color = f"{COLORS[self.coloring[y][x] % (len(COLORS)-1) + 1]}"
                if self.coloring[y][x] == 0:
                    color = f"{COLORS[0]}"
                text = f"{text}{color}{self.heightmap[y][x]}{COLOR_RESET}"
            text = f"{text}\n"
        return text


def main():
    with open(filename, "r") as f:
        # parse input
        cave = LavaCave(f.readlines())
        logging.debug(f"Cave layout ({cave.xheight()}, {cave.yheight()}):\n{str(cave)}")

        # part 1
        logging.info(f"Lowpoint sum: {cave.get_riskfactor()}")

        # part 2
        logging.debug(f"Basin sizes: {list(cave.get_basin_sizes())}")
        logging.info(
            f"Riskfactor by top 3 basin sizes: {cave.get_riskfactor_by_basins()}"
        )


main()