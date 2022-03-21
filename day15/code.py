from __future__ import annotations
import sys, os, copy
import logging
from typing import Deque, Dict, Generator, List, Set, Tuple
import heapq

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


def parse_input(
    input: List[str],
) -> Tuple[Dict[Tuple[int, int], int], int, int]:
    map: Dict[Tuple[int, int], int] = {}
    width: int = 0
    height: int = 0

    for y, line in enumerate([l.strip() for l in input]):
        height = max(height, y + 1)
        for x, cost in enumerate(list(line)):
            map[(x, y)] = int(cost)
            width = max(width, x + 1)

    return map, width, height


def extend_map(
    costs: Dict[Tuple[int, int], int], width: int, height: int, repetition: int
) -> Tuple[Dict[Tuple[int, int], int], int, int]:
    new_map: Dict[Tuple[int, int], int] = {}

    for rx in range(repetition):
        for ry in range(repetition):
            for x, y in costs.keys():
                new_value = (costs[(x, y)] + rx + ry - 1) % 9 + 1
                new_map[(rx * width + x, ry * height + y)] = new_value

    return new_map, width * repetition, height * repetition


def neighbors_of_position(costs: Dict[Tuple[int, int], int], pos: Tuple[int, int]):
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if (pos[0] + dx, pos[1] + dy) in costs:
            yield (pos[0] + dx, pos[1] + dy)
    return []


def dijkstra(
    costs: Dict[Tuple[int, int], int], width: int, height: int
) -> List[Tuple[int, int]]:
    open_nodes: List[Tuple[int, int, int, List[Tuple[int, int]]]] = []
    closed_nodes: Set[Tuple[int, int]] = set()

    open_nodes.append((0, 0, 0, []))

    return_path = []
    while len(open_nodes) > 0:
        current_distance, current_x, current_y, return_path = heapq.heappop(open_nodes)
        current_node = (current_x, current_y)
        if current_node in closed_nodes:
            continue
        if current_node == (width - 1, height - 1):
            break

        closed_nodes.add(current_node)

        for x in neighbors_of_position(costs, current_node):
            if x in closed_nodes:
                continue

            new_distance = current_distance + costs[x]
            heapq.heappush(
                open_nodes,
                (new_distance, x[0], x[1], list(return_path) + [(x[0], x[1])]),
            )

    return return_path


def visualize_path(costs, width, height, path) -> str:
    text = ""

    for y in range(height):
        for x in range(width):
            if (x, y) in path:
                text = f"{text}{COLORS_RED}{costs[(x,y)]}{COLOR_RESET}"
            else:
                text = f"{text}{costs[(x,y)]}"
        text = f"{text}\n"

    return text


def main():
    with open(filename, "r") as f:
        costs, width, height = parse_input(f.readlines())
        path = dijkstra(costs, width, height)
        logging.debug(
            "Path:\n%s",
            visualize_path(costs, width, height, path),
        )
        final_cost = sum([costs[pos] for pos in path])
        logging.info("Risk cost of path is %d", final_cost)

        costs, width, height = extend_map(costs, width, height, 5)
        path = dijkstra(costs, width, height)
        logging.debug(
            "Path:\n%s",
            visualize_path(costs, width, height, path),
        )
        final_cost = sum([costs[pos] for pos in path])
        logging.info("Risk cost of path is %d", final_cost)


main()