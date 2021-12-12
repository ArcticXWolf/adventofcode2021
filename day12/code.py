from __future__ import annotations
import sys, os
import logging
from typing import Dict, Generator, List, Set, Tuple
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


class CaveSystem:
    connections: Dict[str, Set[str]]

    def __init__(self, input: List[str]) -> None:
        self.connections = {}
        for line in input:
            a, b = line.strip().split("-")
            if a not in self.connections:
                self.connections[a] = set()
            if b not in self.connections:
                self.connections[b] = set()
            self.connections[a].add(b)
            self.connections[b].add(a)

        if (
            "start" not in self.connections.keys()
            or "end" not in self.connections.keys()
        ):
            raise Exception("start or end not in connections")

    def calculate_paths(self, allow_small_caves_twice: bool = False) -> List[List[str]]:
        return self.iterate_path(
            ["start"],
            {x: 0 for x in self.connections.keys() if x.islower()},
            allow_small_caves_twice,
        )

    def iterate_path(
        self,
        current_path: List[str],
        blacklist: Dict[str, int],
        allow_small_caves_twice: bool = False,
    ) -> List[List[str]]:
        if current_path[-1] == "end":
            return [[x for x in current_path]]

        if current_path[-1].islower():
            blacklist[current_path[-1]] += 1

        neighbors = [
            node
            for node in self.connections[current_path[-1]]
            if not node.islower()
            or blacklist[node] == 0
            or (
                allow_small_caves_twice
                and all(x < 2 for x in blacklist.values())
                and node != "start"
                and node != "end"
            )
        ]

        if len(neighbors) == 0:
            if current_path[-1].islower():
                blacklist[current_path[-1]] -= 1
            return []

        result_paths = []
        for node in neighbors:
            current_path.append(node)
            result_paths.extend(
                self.iterate_path(current_path, blacklist, allow_small_caves_twice)
            )
            current_path.pop()

        if current_path[-1].islower():
            blacklist[current_path[-1]] -= 1

        return result_paths

    def __str__(self) -> str:
        return str(self.connections)


def main():
    with open(filename, "r") as f:
        system = CaveSystem(f.readlines())
        logging.debug(f"CaveSystem connections:\n{str(system)}")
        paths = system.calculate_paths(allow_small_caves_twice=False)
        logging.debug(f"CaveSystem paths ({len(paths)} paths):")
        for path in paths:
            logging.debug(f"Path: {path}")

        logging.info(f"Cavesystem has {len(paths)} paths.")

        paths = system.calculate_paths(allow_small_caves_twice=True)
        logging.debug(f"CaveSystem2 paths ({len(paths)} paths):")
        for path in paths:
            logging.debug(f"Path: {path}")

        logging.info(f"Cavesystem2 has {len(paths)} paths.")


main()