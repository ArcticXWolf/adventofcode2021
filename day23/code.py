from __future__ import annotations
import itertools
import sys, os, re, numpy, functools, copy
from unittest import result
import logging
from typing import Any, Dict, List, Tuple

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
LINE_REGEX = re.compile(".*#(\w)#(\w)#(\w)#(\w)#.*")
INVALID_COST = 1000000000000


class PuzzleCache:
    def __init__(self) -> None:
        self.cache = {}

    def reset(self):
        self.cache = {}

    def add(self, hallway, rooms):
        hash_value = hash(
            (tuple(hallway), ((k, tuple(v)) for k, v in sorted(rooms.items())))
        )
        self.cache[hash_value] = (copy.deepcopy(hallway), copy.deepcopy(rooms))

    def get(self, hallway, rooms) -> bool:
        hash_value = hash(
            (tuple(hallway), ((k, tuple(v)) for k, v in sorted(rooms.items())))
        )
        if hash_value not in self.cache:
            return False

        return (
            self.cache[hash_value][0] == hallway and self.cache[hash_value][1] == rooms
        )


class Puzzle:
    rooms: Dict[str, List[str]]
    hallway: List[str]

    def __init__(self, lines) -> None:
        self.cache = PuzzleCache()
        self.action_stack = []
        self.hallway = ["."] * 11
        self.rooms = {"A": [], "B": [], "C": [], "D": []}
        self.hallway_entrances = {
            "A": 2,
            "B": 4,
            "C": 6,
            "D": 8,
        }
        self.pod_movement_cost = {
            "A": 1,
            "B": 10,
            "C": 100,
            "D": 1000,
        }

        for line in lines:
            matches = re.match(LINE_REGEX, line)
            if not matches:
                continue

            for index, key in enumerate(self.rooms.keys()):
                self.rooms[key].append(matches.group(index + 1))

    def possible_actions(self) -> List[Tuple[Tuple[str, int], Tuple[str, int]]]:
        possible_sources = []
        for k, r in self.rooms.items():
            for pos, value in enumerate(r):
                if all(x == k or x == "." for x in r):
                    break  # solved rooms do not move anymore
                if value != ".":
                    possible_sources.append((k, pos))
                    break  # because only the topmost pod can move
        possible_sources.extend(
            [("hallway", pos) for pos, value in enumerate(self.hallway) if value != "."]
        )

        possible_actions = []
        for source_origin, source_position in possible_sources:
            possible_actions.extend(
                self._possible_actions_to_room_for_source(
                    source_origin, source_position
                )
            )
            if source_origin != "hallway":
                possible_actions.extend(
                    self._possible_actions_to_hallway_for_source(
                        source_origin, source_position
                    )
                )

        return possible_actions

    def _possible_actions_to_room_for_source(
        self, source_origin, source_position
    ) -> List[Tuple[Tuple[str, int], Tuple[str, int], int]]:
        pod_type = (
            self.hallway[source_position]
            if source_origin == "hallway"
            else self.rooms[source_origin][source_position]
        )

        # only move into destination room from hallway
        for target_pos, target_value in reversed(list(enumerate(self.rooms[pod_type]))):
            if target_value == ".":
                valid, cost = self.simulate_movement(
                    pod_type, source_origin, source_position, pod_type, target_pos
                )
                if not valid:
                    return []
                return [
                    ((source_origin, source_position), (pod_type, target_pos), cost)
                ]
            if target_value != pod_type:
                break

        return []

    def _possible_actions_to_hallway_for_source(
        self, source_origin, source_position
    ) -> List[Tuple[Tuple[str, int], Tuple[str, int], int]]:
        pod_type = (
            self.hallway[source_position]
            if source_origin == "hallway"
            else self.rooms[source_origin][source_position]
        )
        possible_actions = []

        for pos, hallway_value in enumerate(self.hallway):
            if hallway_value != ".":  # only move to empty pos
                continue
            if pos in self.hallway_entrances.values():  # do not move to room entrances
                continue
            valid, cost = self.simulate_movement(
                pod_type, source_origin, source_position, "hallway", pos
            )
            if not valid:
                continue
            possible_actions.append(
                ((source_origin, source_position), ("hallway", pos), cost)
            )

        return possible_actions

    def simulate_movement(
        self,
        pod_type: str,
        source_origin: str,
        source_position: int,
        target_origin: str,
        target_position: int,
    ) -> Tuple[bool, int]:
        cost = 0

        # move out of room
        if source_origin != "hallway":
            for room_pos, room_value in reversed(
                list(enumerate(self.rooms[source_origin]))
            ):
                if room_pos >= source_position:
                    continue

                if room_value == ".":
                    cost += 1
                else:
                    return False, INVALID_COST
            cost += 1

        # move through hallway
        hallway_start = (
            source_position
            if source_origin == "hallway"
            else self.hallway_entrances[source_origin]
        )
        hallway_destination = (
            target_position
            if target_origin == "hallway"
            else self.hallway_entrances[target_origin]
        )

        for pos in range(
            hallway_destination,
            hallway_start,
            1 if hallway_destination < hallway_start else -1,
        ):
            if self.hallway[pos] == ".":
                cost += 1
            else:
                return False, INVALID_COST

        # move into room
        if target_origin != "hallway":
            for room_pos, room_value in enumerate(self.rooms[target_origin]):
                if room_pos > target_position:
                    continue

                if room_value == ".":
                    cost += 1
                else:
                    return False, INVALID_COST

        return True, cost * self.pod_movement_cost[pod_type]

    def do_action(self, source, target, cost):
        pod_type = (
            self.hallway[source[1]]
            if source[0] == "hallway"
            else self.rooms[source[0]][source[1]]
        )
        if source[0] == "hallway":
            self.hallway[source[1]] = "."
        else:
            self.rooms[source[0]][source[1]] = "."
        if target[0] == "hallway":
            self.hallway[target[1]] = pod_type
        else:
            self.rooms[target[0]][target[1]] = pod_type

        if cost > 0:
            self.action_stack.append((source, target, cost))

    def undo_action(self):
        source, target, _ = self.action_stack.pop()
        self.do_action(target, source, -1)

    def depth_search_solutions(
        self,
        best_cost: int = INVALID_COST,
    ) -> Tuple[List[Tuple[Tuple[str, int], Tuple[str, int], int]], int]:
        if self.is_solved():
            logging.debug("Solution found: %d", self.current_action_cost())
            logging.debug("%s", self.str_action_stack())
            logging.debug("%s", str(self))
            return (copy.deepcopy(self.action_stack), self.current_action_cost())

        cache_available = self.cache.get(self.hallway, self.rooms)
        if cache_available:
            return ([], INVALID_COST)

        result = ([], INVALID_COST)
        for source, target, cost in self.possible_actions():
            if self.current_action_cost() + cost >= best_cost:
                continue
            self.do_action(source, target, cost)
            new_result = self.depth_search_solutions(best_cost)
            if len(new_result[0]) > 0 and new_result[1] < best_cost:
                result = new_result
                best_cost = new_result[1]
            self.undo_action()

        if result[1] == INVALID_COST:
            self.cache.add(self.hallway, self.rooms)

        return result

    def current_action_cost(self):
        return sum(cost for _, _, cost in self.action_stack)

    def is_solved(self) -> bool:
        return (
            all(x == "." for x in self.hallway)
            and all(x == "A" for x in self.rooms["A"])
            and all(x == "B" for x in self.rooms["B"])
            and all(x == "C" for x in self.rooms["C"])
            and all(x == "D" for x in self.rooms["D"])
        )

    def str_action_stack(self) -> str:
        text = "Stack:\n"
        for x, y, c in self.action_stack:
            text += f"{str(x)} {str(y)} {c}\n"
        return text

    def __str__(self) -> str:
        text = f"#############\n"
        text += f"#{''.join(self.hallway)}#\n"
        for index in range(len(self.rooms["A"])):
            text += f"###{self.rooms['A'][index]}#{self.rooms['B'][index]}#{self.rooms['C'][index]}#{self.rooms['D'][index]}###\n"
        text += f"#############\n"
        return text


def main():
    with open(filename, "r") as f:
        lines = [x.strip() for x in f.readlines()]
        puzzle = Puzzle(lines)
        logging.debug("Puzzle input: \n%s", puzzle)

        result, cost = puzzle.depth_search_solutions()
        logging.debug("Solution: %d\n%s", cost, "\n".join(str(x) for x in result))

        # puzzle.do_action(("D", 0), ("hallway", 10), -1)
        # puzzle.do_action(("C", 0), ("hallway", 9), -1)
        # puzzle.do_action(("D", 1), ("hallway", 0), -1)
        # puzzle.do_action(("C", 1), ("hallway", 7), -1)
        # puzzle.do_action(("C", 2), ("hallway", 1), -1)
        # logging.debug("%s", puzzle)
        # logging.debug("%s", puzzle.possible_actions())


main()