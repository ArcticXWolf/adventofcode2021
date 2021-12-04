from typing import List, Tuple
import sys, os
import logging
from enum import Enum

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)


class Direction(Enum):
    ROW = 0
    COLUMN = 1


class BingoBoard:
    board: List[List[int]]
    markers: List[List[bool]]
    xsize: int
    ysize: int

    def __init__(self, input_rows: List[str]) -> None:
        self.board = []
        self.markers = []
        for input_row in input_rows:
            row = [int(x) for x in input_row.strip().split()]
            self.board.append(row)

            marker = [False for x in input_row.strip().split()]
            self.markers.append(marker)
        self.xsize = len(self.board[0])
        self.ysize = len(self.board)

    def __str__(self) -> str:
        text = ""
        for ri, row in enumerate(self.board):
            for ci, column in enumerate(row):
                marker = "M" if self.markers[ri][ci] else " "
                text = f"{text}{marker}{column:03d} "
            text = f"{text}\n"
        return text

    def mark_number(self, number: int):
        for ri, row in enumerate(self.board):
            for ci, column in enumerate(row):
                if column == number:
                    self.markers[ri][ci] = True

    def get_winnings(self) -> List[Tuple[Direction, int]]:
        row_winnings = [(Direction.ROW, x) for x in self.get_row_winnings()]
        column_winnings = [(Direction.COLUMN, x) for x in self.get_column_winnings()]
        row_winnings.extend(column_winnings)
        return row_winnings

    def get_row_winnings(self) -> List[int]:
        winning_rows = []
        for ri in range(self.ysize):
            is_full = True
            for ci in range(self.xsize):
                if not self.markers[ri][ci]:
                    is_full = False
                    break

            if is_full:
                winning_rows.append(ri)
        return winning_rows

    def get_column_winnings(self) -> List[int]:
        winning_cols = []
        for ci in range(self.xsize):
            is_full = True
            for ri in range(self.ysize):
                if not self.markers[ri][ci]:
                    is_full = False
                    break

            if is_full:
                winning_cols.append(ri)
        return winning_cols

    def get_score(self, last_number: int) -> int:
        score = 0
        for ri in range(self.ysize):
            for ci in range(self.xsize):
                if not self.markers[ri][ci]:
                    score += self.board[ri][ci]
        return score * last_number


def main():
    numbers = []
    boards = []
    boards_won = []
    with open(filename, "r") as f:
        numbers, boards = parse_input([x.strip() for x in f.readlines()])
        boards_won = list(range(len(boards)))

    logging.debug(f"Numbers: {numbers}")
    for board in boards:
        logging.debug(f"Board: \n{str(board)}")

    for number in numbers:
        for index, board in enumerate(boards):
            board.mark_number(number)
            win = board.get_winnings()
            if len(win) > 0:

                # first winning board
                if len(boards) == len(boards_won):
                    logging.info(f"WINNING Board: \n{str(board)}")
                    logging.info(f"WIN by: {str(win)}")
                    logging.info(f"WIN score: {board.get_score(number)}\n\n")

                # last winning board
                if len(boards_won) == 1 and index in boards_won:
                    logging.info(f"LOSING Board: \n{str(board)}")
                    logging.info(f"WIN by: {str(win)}")
                    logging.info(f"WIN score: {board.get_score(number)}\n\n")
                    return

                try:
                    boards_won.remove(index)
                except:
                    pass


def parse_input(input: List[str]) -> Tuple[List[int], List[BingoBoard]]:
    numbers = [int(x) for x in input.pop(0).split(",")]
    boards = []

    input.pop(0)  # remove blank line before first board
    if input[-1] != "":
        input.append("")  # append blank line for board detection

    board_input = []
    while len(input) > 0:
        board_input.append(input.pop(0))
        if input[0] == "":
            input.pop(0)
            boards.append(BingoBoard(board_input))
            board_input = []

    return (numbers, boards)


main()