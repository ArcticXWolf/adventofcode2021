from __future__ import annotations
from dis import Instruction
import itertools
import sys, os, re, numpy, functools, copy
from unittest import result
import logging
from typing import Any, Dict, List, Set, Tuple

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
LINE_REGEX = re.compile(
    "(on|off) x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)"
)


def parse_instructions(lines):
    instructions = []
    for line in lines:
        matches = re.match(LINE_REGEX, line)
        if not matches:
            raise Exception("Malformed input")
        instructions.append(
            (
                matches.group(1),
                (int(matches.group(2)), int(matches.group(4)), int(matches.group(6))),
                (
                    int(matches.group(3)) + 1,
                    int(matches.group(5)) + 1,
                    int(matches.group(7)) + 1,
                ),
            )
        )
    return instructions


def execute_instruction(board: Set[Tuple[int, int, int]], instruction, size):
    f = board.add
    if instruction[0] == "off":
        f = board.remove
    for x in range(instruction[1][0], instruction[2][0] + 1):
        if size > 0 and not (-size <= x <= size):
            continue
        for y in range(instruction[1][1], instruction[2][1] + 1):
            if size > 0 and not (-size <= y <= size):
                continue
            for z in range(instruction[1][2], instruction[2][2] + 1):
                if size > 0 and not (-size <= z <= size):
                    continue
                try:
                    f((x, y, z))
                except KeyError:
                    pass


def create_cube_boundaries(instructions):
    boundaries = []
    for _ in instructions[0][1]:
        boundaries.append({-50, 50})

    for instruction in instructions:
        for i, _ in enumerate(boundaries):
            boundaries[i].add(instruction[1][i])
            boundaries[i].add(instruction[2][i])

    return [
        [
            (start, end)
            for start, end in zip(sorted(dimension)[:-1], sorted(dimension)[1:])
        ]
        for dimension in boundaries
    ]


def calculate_active_cubes(boundaries, instructions):
    number_of_active_cubes = 0
    number_of_active_init_cubes = 0
    for i, (xstart, xend) in enumerate(boundaries[0]):
        logging.debug("Analyzed %d/%d", i, len(boundaries[0]))
        instructions_of_x = [
            instruction
            for instruction in instructions
            if instruction[1][0] <= xstart < instruction[2][0]
            and instruction[1][0] < xend <= instruction[2][0]
        ]
        for ystart, yend in boundaries[1]:
            instructions_of_y = [
                instruction
                for instruction in instructions_of_x
                if instruction[1][1] <= ystart < instruction[2][1]
                and instruction[1][1] < yend <= instruction[2][1]
            ]
            for zstart, zend in boundaries[2]:
                instructions_of_cube = [
                    instruction
                    for instruction in instructions_of_y
                    if instruction[1][2] <= zstart < instruction[2][2]
                    and instruction[1][2] < zend <= instruction[2][2]
                ]

                # logging.debug(
                #     "Cube on: %d..%d %d..%d %d..%d: %s",
                #     xstart,
                #     xend,
                #     ystart,
                #     yend,
                #     zstart,
                #     zend,
                #     str(instructions_of_cube),
                # )

                if len(instructions_of_cube) <= 0:
                    continue

                if instructions_of_cube[-1][0] == "off":
                    continue

                if (
                    -50 <= xstart < 51
                    and -50 < xend <= 51
                    and -50 <= ystart < 51
                    and -50 < yend <= 51
                    and -50 <= zstart < 51
                    and -50 < zend <= 51
                ):
                    number_of_active_init_cubes += (
                        abs(xend - xstart) * abs(yend - ystart) * abs(zend - zstart)
                    )

                number_of_active_cubes += (
                    abs(xend - xstart) * abs(yend - ystart) * abs(zend - zstart)
                )
    return number_of_active_cubes, number_of_active_init_cubes


def main():
    with open(filename, "r") as f:
        lines = [x.strip() for x in f.readlines()]
        instructions = parse_instructions(lines)
        boundaries = create_cube_boundaries(instructions)
        logging.debug(
            "Boundaries:\n%s\n%s\n%s\n",
            str(boundaries[0]),
            str(boundaries[1]),
            str(boundaries[2]),
        )
        result, result_init = calculate_active_cubes(boundaries, instructions)
        logging.info("Amount of active init cubes: %d", result_init)
        logging.info("Amount of active cubes: %d", result)


main()