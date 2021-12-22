from __future__ import annotations
import sys, os, re, numpy
import logging
from typing import Dict, List, Tuple

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
LINE_REGEX = re.compile("(-?\d+),(-?\d+),(-?\d+)")


def main():
    with open(filename, "r") as f:
        # setup
        scanner_beacons = parse_input(f.readlines())
        scanner_distances = calculate_distances(scanner_beacons)
        transformation_dict = depth_search_overlap_transformation_matrices(
            scanner_distances, 0, {}, numpy.identity(4)
        )

        # part 1
        beacons = transform_beacons_to_default_space(
            scanner_beacons, transformation_dict
        )
        logging.info("There are %d beacons in total.", len(beacons))

        # part 2
        max_distance, pair = calculate_max_scanner_distance(transformation_dict)
        logging.info("Maximum distance is %d with pair %s.", max_distance, pair)


def parse_input(input) -> Dict[int, List[numpy.array]]:
    scanner_beacons = {}
    index = -1
    for line in input:
        line = line.strip()
        if line == "":
            continue

        if line.startswith("---"):
            index += 1
            scanner_beacons[index] = []
            continue

        matches = LINE_REGEX.match(line)
        if matches == None:
            raise Exception(f"line input malformed: {line}")
        scanner_beacons[index].append(
            numpy.array(
                (
                    int(matches.group(1)),
                    int(matches.group(2)),
                    int(matches.group(3)),
                )
            )
        )
    return scanner_beacons


def calculate_distances(
    scanner_beacons,
) -> Dict[int, List[Tuple[int, numpy.array, numpy.array]]]:
    scanner_distances = {}
    for id, sb in scanner_beacons.items():
        scanner_distances[id] = {
            tuple(b): [numpy.linalg.norm(a - b) for a in sb if tuple(a) != tuple(b)]
            for b in sb
        }
    return scanner_distances


def match_relative_beacons(scanner_distances, i, j):
    beacon_map = {}
    for bi, di in scanner_distances[i].items():
        for bj, dj in scanner_distances[j].items():
            if len(numpy.intersect1d(di, dj)) >= 11:
                beacon_map[bi] = bj
    return beacon_map


def calculate_transformation_matric(beacon_map):
    source_matrix = numpy.stack([numpy.array(x) for x in beacon_map.values()], axis=1)
    source_matrix = numpy.concatenate(
        [source_matrix, numpy.ones_like(source_matrix[:1])], axis=0
    )
    destination_matrix = numpy.stack(
        [numpy.array(x) for x in beacon_map.keys()], axis=1
    )
    destination_matrix = numpy.concatenate(
        [destination_matrix, numpy.ones_like(destination_matrix[:1])], axis=0
    )

    transformation_matrix, resid, rank, sing = numpy.linalg.lstsq(
        source_matrix.T, destination_matrix.T, rcond=None
    )
    transformation_matrix = numpy.rint(transformation_matrix.T).astype(int)

    return transformation_matrix


def depth_search_overlap_transformation_matrices(
    scanner_distances,
    own_id,
    running_transformation_dict,
    previous_transformation_matrix,
):
    transformation_dict = {own_id: previous_transformation_matrix}
    transformation_dict.update(running_transformation_dict)
    to_search = [x for x in scanner_distances.keys() if x not in transformation_dict]

    for s in to_search:
        beacon_map = match_relative_beacons(scanner_distances, own_id, s)

        if len(beacon_map) < 12:
            continue

        logging.debug("s%d with s%d has %d beacons aligned", own_id, s, len(beacon_map))
        transformation_matrix = calculate_transformation_matric(beacon_map)
        logging.debug(
            "s%d has coords: %s",
            s,
            tuple(
                previous_transformation_matrix
                @ transformation_matrix
                @ numpy.array([0, 0, 0, 1])
            ),
        )

        new_transformation_dict = depth_search_overlap_transformation_matrices(
            scanner_distances,
            s,
            transformation_dict,
            previous_transformation_matrix @ transformation_matrix,
        )
        transformation_dict.update(new_transformation_dict)

    return transformation_dict


def transform_beacons_to_default_space(scanner_beacons, transformation_dict):
    beacons = set()
    for s, sbs in scanner_beacons.items():
        for beacon in sbs:
            beacon_coords = numpy.concatenate(
                [numpy.array(beacon), numpy.array([1])], axis=0
            )
            absolute_coords = transformation_dict[s] @ beacon_coords
            beacons.add(tuple(absolute_coords.astype(int)))

    for b in sorted(beacons):
        logging.debug("%s", b)
    return beacons


def calculate_max_scanner_distance(transformation_dict):
    scanner_coordinates = {}
    for s, t in transformation_dict.items():
        scanner_coordinates[s] = tuple(t @ numpy.array([0, 0, 0, 1]))

    for s, b in scanner_coordinates.items():
        logging.debug("%s %s", s, b)

    max_distance = 0
    pair = []
    for s1, v1 in scanner_coordinates.items():
        for s2, v2 in scanner_coordinates.items():
            distance = abs(v1[0] - v2[0])
            distance += abs(v1[1] - v2[1])
            distance += abs(v1[2] - v2[2])
            if distance > max_distance:
                max_distance = distance
                pair = [s1, s2]
    return max_distance, pair


main()