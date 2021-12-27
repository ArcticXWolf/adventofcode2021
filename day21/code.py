from __future__ import annotations
import sys, os, re, numpy, itertools
import logging
from typing import Dict, List, Tuple

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"
LINE_REGEX = re.compile("Player (\d+) starting position: (\d+)")


def main():
    with open(filename, "r") as f:
        lines = [x.strip() for x in f.readlines()]
        part1(lines)
        part2(lines)


def part1(lines):
    # part 1
    player_pos = {}
    for line in lines:
        matches = LINE_REGEX.match(line)
        if matches == None:
            raise Exception(f"line input malformed: {line}")
        player_pos[int(matches.group(1))] = int(matches.group(2))

    player_score = {i: 0 for i in player_pos.keys()}
    dice_value = 1
    rolls = 0
    current_player = min(player_pos.keys())
    while all(x < 1000 for x in player_score.values()):
        player_pos[current_player] = player_pos[current_player] + dice_value * 3 + 3
        player_pos[current_player] = mod_with_one(player_pos[current_player], 10)
        logging.debug(
            "Player %d rolls %d+%d+%d (%d) and moves to space %d for a total score of %d",
            current_player,
            dice_value,
            dice_value + 1,
            dice_value + 2,
            dice_value * 3 + 3,
            player_pos[current_player],
            player_score[current_player] + player_pos[current_player],
        )
        dice_value += 3
        dice_value = mod_with_one(dice_value, 100)
        rolls += 3
        player_score[current_player] += player_pos[current_player]
        current_player = mod_with_one(current_player + 1, len(player_pos.keys()))

    logging.info(
        "Number of rolls %d, result %d",
        rolls,
        [s for _, s in player_score.items() if s < 1000][0] * rolls,
    )


def part2(lines):
    player_pos = {}
    for line in lines:
        matches = LINE_REGEX.match(line)
        if matches == None:
            raise Exception(f"line input malformed: {line}")
        player_pos[int(matches.group(1))] = int(matches.group(2))

    paths_to_state = {(0, player_pos[1], player_pos[2], 0, 0): 1}
    p0_wins = 0
    p1_wins = 0

    while len(paths_to_state) > 0:
        current_state = list(paths_to_state.keys())[0]
        turn, p0p, p1p, p0s, p1s = current_state
        count_universes = paths_to_state[current_state]
        del paths_to_state[current_state]

        if p0s >= 21:
            p0_wins += count_universes
            continue
        if p1s >= 21:
            p1_wins += count_universes
            continue

        for x in [
            3,
            4,
            4,
            4,
            5,
            5,
            5,
            5,
            5,
            5,
            6,
            6,
            6,
            6,
            6,
            6,
            6,
            7,
            7,
            7,
            7,
            7,
            7,
            8,
            8,
            8,
            9,
        ]:
            if turn == 0:
                new_state = (
                    1,
                    mod_with_one(p0p + x, 10),
                    p1p,
                    p0s + mod_with_one(p0p + x, 10),
                    p1s,
                )
                if new_state not in paths_to_state:
                    paths_to_state[new_state] = 0
                paths_to_state[new_state] += count_universes
            if turn == 1:
                new_state = (
                    0,
                    p0p,
                    mod_with_one(p1p + x, 10),
                    p0s,
                    p1s + mod_with_one(p1p + x, 10),
                )
                if new_state not in paths_to_state:
                    paths_to_state[new_state] = 0
                paths_to_state[new_state] += count_universes

    logging.info(
        "P1 Wins %d, P2 Wins %d, P1 more than P2? %s",
        p0_wins,
        p1_wins,
        p0_wins > p1_wins,
    )


def mod_with_one(value, mod):
    return ((value - 1) % mod) + 1


main()