from __future__ import annotations
import sys, os, re, numpy, itertools, time
import logging
from typing import Dict, List, Tuple, Generator
from enum import Enum

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS = [f"\x1b[38;5;{d}m" for d in range(124, 232, 16)]
COLOR_RESET = "\x1b[0m"


class Position(Enum):
    Empty = "."
    South = "v"
    East = ">"


class Board:
    grid: Dict[Tuple[int, int], Position]
    movable: Dict[Position, List[Tuple[int, int]]]

    def __init__(self, lines) -> None:
        self.grid = {}
        self.movable = {Position.Empty: [], Position.East: [], Position.South: []}
        self.width = 0
        self.height = len(lines)
        for y, line in enumerate(lines):
            self.width = max(self.width, len(line))
            for x, character in enumerate(list(line)):
                self.grid[(x, y)] = Position(character)
        self.update_all_movable_positions_of_type(Position.East)
        self.update_all_movable_positions_of_type(Position.South)

    def all_positions_of_type(self, postype: Position):
        return ((k[0], k[1]) for k, v in self.grid.items() if v == postype)

    def update_all_movable_positions_of_type(self, postype: Position):
        if postype == Position.Empty:
            self.movable[postype] = []
            return

        direction = (1, 0)
        if postype == Position.South:
            direction = (0, 1)

        self.movable[postype] = [
            (x, y)
            for x, y in self.all_positions_of_type(postype)
            if self.grid[
                ((x + direction[0]) % self.width, (y + direction[1]) % self.height)
            ]
            == Position.Empty
        ]

    def move_all_positions_of_type(self, postype: Position):
        if postype == Position.Empty:
            return []
        direction = (1, 0)
        if postype == Position.South:
            direction = (0, 1)
        for x, y in self.movable[postype]:
            self.grid[
                ((x + direction[0]) % self.width, (y + direction[1]) % self.height)
            ] = postype
            self.grid[(x, y)] = Position.Empty
        self.update_all_movable_positions_of_type(Position.East)
        self.update_all_movable_positions_of_type(Position.South)

    def move_once(self):
        self.move_all_positions_of_type(Position.East)
        self.move_all_positions_of_type(Position.South)

    def move_until_stops(self):
        steps = 0
        while (
            len(self.movable[Position.East]) > 0
            or len(self.movable[Position.South]) > 0
        ):
            self.move_once()
            steps += 1

            if steps % 10 == 0:
                logging.debug("Board (at %d):\n%s", steps, str(self))
        return steps

    def __str__(self) -> str:
        text = ""
        for y in range(self.height):
            for x in range(self.width):
                east = (x, y) in self.movable[Position.East]
                south = (x, y) in self.movable[Position.South]
                if east:
                    text += COLORS[0]
                if south:
                    text += COLORS[1]
                text += self.grid[(x, y)].value
                if south or east:
                    text += COLOR_RESET
            text += "\n"
        return text


def main():
    with open(filename, "r") as f:
        lines = [x.strip() for x in f.readlines()]
        board = Board(lines)
        logging.debug("Board:\n%s", str(board))
        steps = board.move_until_stops()
        logging.debug("Board:\n%s", str(board))
        logging.info("Steps taken:\n%d", steps + 1)


main()