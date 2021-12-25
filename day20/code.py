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
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


def main():
    with open(filename, "r") as f:
        image_algo = []
        for character in list(f.readline().strip()):
            if character == "#":
                image_algo.append(True)
            else:
                image_algo.append(False)
        f.readline()

        grid = {}
        for y, line in enumerate(f.readlines()):
            for x, character in enumerate(list(line.strip())):
                grid[(x, y)] = True if character == "#" else False

        unset_pixels_default = False

        logging.debug(
            "RAW IMAGE: %d lit \n%s\n\n",
            get_lit_pixels(grid),
            get_grid_str(grid, unset_pixels_default),
        )

        for i in range(50):
            grid = enhance_image(grid, image_algo, unset_pixels_default)
            unset_pixels_default = flip_default_value(image_algo, unset_pixels_default)
            if i == 1 or i == 49:
                logging.info(
                    "Enhanced IMAGE #%d: %d lit \n%s\n\n",
                    i + 1,
                    get_lit_pixels(grid),
                    get_grid_str(grid, unset_pixels_default),
                )


def flip_default_value(image_algo, unset_pixels_default):
    if not unset_pixels_default and image_algo[0]:
        return True
    if not unset_pixels_default and not image_algo[0]:
        return False
    if unset_pixels_default and not image_algo[-1]:
        return False
    if unset_pixels_default and image_algo[-1]:
        return True
    return False


def enhance_image(grid, image_algo, unset_pixels_default=False):
    enhanced_grid = {}
    start_x = min(grid, key=lambda t: t[0])[0] - 2
    start_y = min(grid, key=lambda t: t[1])[1] - 2
    stop_x = max(grid, key=lambda t: t[0])[0] + 2
    stop_y = max(grid, key=lambda t: t[1])[1] + 2

    for y in range(start_y, stop_y + 1):
        for x in range(start_x, stop_x + 1):
            index = get_algo_index_by_position(grid, x, y, unset_pixels_default)
            enhanced_grid[(x, y)] = image_algo[index]

    return enhanced_grid


def get_algo_index_by_position(grid, x, y, unset_pixels_default) -> int:
    index_bitstring = ""
    for dx, dy in [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (0, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]:
        if (x + dx, y + dy) not in grid:
            if unset_pixels_default == False:
                index_bitstring += "0"
            else:
                index_bitstring += "1"
            continue
        if grid[(x + dx, y + dy)]:
            index_bitstring += "1"
        else:
            index_bitstring += "0"
    return int(index_bitstring, 2)


def get_grid_str(grid, unset_pixels_default):
    start_x = min(grid, key=lambda t: t[0])[0] - 2
    start_y = min(grid, key=lambda t: t[1])[1] - 2
    stop_x = max(grid, key=lambda t: t[0])[0] + 2
    stop_y = max(grid, key=lambda t: t[1])[1] + 2
    image_string = ""

    for y in range(start_y, stop_y + 1):
        for x in range(start_x, stop_x + 1):
            if (x, y) == (0, 0):
                image_string += COLORS_RED
            if (x, y) in grid and grid[(x, y)]:
                image_string += "#"
            elif (x, y) in grid:
                image_string += "."
            else:
                if unset_pixels_default == False:
                    image_string += "."
                else:
                    image_string += "#"

            if (x, y) == (0, 0):
                image_string += COLOR_RESET
        image_string += "\n"

    return image_string


def get_lit_pixels(grid):
    return sum(v for v in grid.values())


main()