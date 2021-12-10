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
OPENPAREN = ["[", "{", "(", "<"]
CLOSEPAREN = {"[": "]", "{": "}", "(": ")", "<": ">"}
PAREN_SYNTAX_SCORE = {")": 3, "]": 57, "}": 1197, ">": 25137}
PAREN_COMPLETE_SCORE = {")": 1, "]": 2, "}": 3, ">": 4}


class InvalidOpenParenthesisError(Exception):
    def __init__(
        self,
        character: str,
        message="invalid character found, but an open parenthesis is expected",
    ):
        self.character = character
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.character} -> {self.message}"


class InvalidCloseParenthesisError(Exception):
    def __init__(
        self,
        open_character: str,
        close_character: str,
        message="invalid closing parenthesis found for the used open parenthesis",
    ):
        self.open_character = open_character
        self.close_character = close_character
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.open_character} - {self.close_character} -> {self.message}"


class IncompleteLineError(Exception):
    def __init__(
        self,
        missing_parens: List[str],
        message="line ended prematurely",
    ):
        self.message = message
        self.missing_parens = missing_parens
        super().__init__(self.message)


def parse_one_chunk(input: List[str], closing_list: List[str]):
    if len(input) == 0 or input[0] in CLOSEPAREN.values():
        return

    open_paren = input.pop(0)
    closing_list.insert(0, CLOSEPAREN[open_paren])

    if open_paren not in OPENPAREN:
        raise InvalidOpenParenthesisError(open_paren)

    while len(input) > 0 and input[0] in OPENPAREN:
        parse_one_chunk(input, closing_list)

    if len(input) == 0:
        raise IncompleteLineError(closing_list)

    close_paren = input.pop(0)
    closing_list.pop(0)
    if close_paren != CLOSEPAREN[open_paren]:
        raise InvalidCloseParenthesisError(open_paren, close_paren)


def parse_chunks(input: List[str]) -> Tuple[int, int]:
    logging.debug(f"Line: {input}")
    try:
        while len(input) > 0:
            parse_one_chunk(input, [])
    except IncompleteLineError as e:
        logging.debug(f"Incomplete line can be completed with {e.missing_parens}\n")
        return (0, calculate_completion_score(e.missing_parens))
    except InvalidCloseParenthesisError as e:
        logging.debug(f"Error: {e}, Score {PAREN_SYNTAX_SCORE[e.close_character]}\n")
        return (PAREN_SYNTAX_SCORE[e.close_character], 0)


def calculate_completion_score(input: List[str]) -> int:
    score = 0
    for x in input:
        score *= 5
        score += PAREN_COMPLETE_SCORE[x]
    return score


def main():
    with open(filename, "r") as f:
        syntax_score = 0
        completion_score = []
        for line in f.readlines():
            characters = list(line.strip())
            sscore, cscore = parse_chunks(characters)
            syntax_score += sscore
            if cscore != 0:
                completion_score.append(cscore)

        logging.info(f"Total syntax error score: {syntax_score}")
        logging.info(
            f"Total autocompletion score: {statistics.median_low(completion_score)}"
        )


main()