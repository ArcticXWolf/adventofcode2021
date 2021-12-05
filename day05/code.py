from __future__ import annotations
from typing import List, Tuple
import sys, os, re
import logging
from enum import Enum

logging.basicConfig(format="%(message)s", level=logging.INFO)
LINE_REGEX = re.compile("(\d+),(\d+) -> (\d+),(\d+)")
sign = lambda x: x and (-1 if x < 0 else 1)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)


class Line:
    startposition: Tuple[int, int]
    endposition: Tuple[int, int]

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.startposition = (x1, y1)
        self.endposition = (x2, y2)

    @classmethod
    def from_string(cls, input: str) -> Line:
        matches = LINE_REGEX.match(input)
        if matches == None:
            raise Exception("line input malformed")
        return cls(
            int(matches.group(1)),
            int(matches.group(2)),
            int(matches.group(3)),
            int(matches.group(4)),
        )

    def get_highest_coordinate(self) -> int:
        return max(
            self.startposition[0],
            self.startposition[1],
            self.endposition[0],
            self.endposition[1],
        )

    def get_direction(self) -> Tuple[int, int]:
        return (
            sign(self.endposition[0] - self.startposition[0]),
            sign(self.endposition[1] - self.startposition[1]),
        )

    def is_vertical(self) -> bool:
        return self.startposition[0] == self.endposition[0]

    def is_horizontal(self) -> bool:
        return self.startposition[1] == self.endposition[1]

    def is_diagonal(self) -> bool:
        return not self.is_horizontal() and not self.is_vertical()


class Board:
    board: List[List[int]]
    lines: List[Line]
    xsize: int
    ysize: int

    def __init__(self, input_lines: List[Line], diagonal_allowed: bool) -> None:
        self.lines = input_lines
        highest_coordinate = 0

        for input_line in input_lines:
            highest_coordinate = max(
                highest_coordinate, input_line.get_highest_coordinate()
            )
        logging.debug(f"Creating board of size: {highest_coordinate}")

        self.xsize = highest_coordinate + 1
        self.ysize = highest_coordinate + 1
        self.board = [[0] * self.ysize for _ in range(self.xsize)]

        for index, line in enumerate(self.lines):
            logging.debug(f"Drawing line #{index} in direction {line.get_direction()}")
            if diagonal_allowed or not line.is_diagonal():
                self.draw_line(line)

    def draw_line(self, line: Line):
        direction = line.get_direction()
        x = line.startposition[0]
        y = line.startposition[1]
        while x != line.endposition[0] or y != line.endposition[1]:
            logging.debug(f"drawing {x},{y}")
            self.board[x][y] += 1
            x += direction[0]
            y += direction[1]
        self.board[x][y] += 1

    def get_amount_of_overlap_points(self) -> int:
        overlaps = 0
        for x in range(self.xsize):
            for y in range(self.ysize):
                if self.board[x][y] > 1:
                    overlaps += 1
        return overlaps

    def __str__(self) -> str:
        text = f"Board ({self.xsize},{self.ysize}) ({self.get_amount_of_overlap_points()} overlaps):\n"
        for y in range(self.ysize):
            for x in range(self.xsize):
                text = f"{text}{self.board[x][y]:01d}"
            text = f"{text}\n"
        return text


def main():
    with open(filename, "r") as f:
        lines = []
        for input in [x.strip() for x in f.readlines()]:
            lines.append(Line.from_string(input))

        board = Board(lines, diagonal_allowed=False)
        logging.debug("%s", board)
        logging.info(
            f"Overlaps without diagonals: {board.get_amount_of_overlap_points()}"
        )

        board = Board(lines, diagonal_allowed=True)
        logging.debug("%s", board)
        logging.info(f"Overlaps with diagonals: {board.get_amount_of_overlap_points()}")


main()