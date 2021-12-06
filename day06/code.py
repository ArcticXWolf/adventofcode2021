from __future__ import annotations
import sys, os
import logging

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)


def main():
    with open(filename, "r") as f:
        numbers = [int(x) for x in f.readline().strip().split(",")]
        # number of active breeding fishs per day of breeding interval (fishs that give birth after 7 days)
        fish_breeding = [0 for _ in range(7)]
        # number of fishs that have the initial growing delay (they get added to fish_breeding after 2 days)
        fish_growing = [0 for _ in range(7)]

        # initial state
        for number in numbers:
            fish_breeding[number] += 1

        # simulate growth
        for current_day in range(256):
            # each breeding fish for today births a new one
            current_births = fish_breeding[current_day % 7]
            # transfer fishs with expired growth delay into breeding pool
            fish_breeding[current_day % 7] += fish_growing[current_day % 7]
            fish_growing[current_day % 7] = 0
            # add todays births to list with growing delay (to be added to breeding pool in 2 days)
            fish_growing[(current_day + 2) % 7] = current_births

            logging.debug(
                f"Growth after {current_day+1:03d} ({current_day % 7:01d}): {sum(fish_growing) + sum(fish_breeding):04d} {fish_breeding} {fish_growing}"
            )

            if current_day + 1 in [18, 80, 256]:
                logging.info(
                    f"Growth after {current_day+1:03d} days: {sum(fish_growing) + sum(fish_breeding):04d}"
                )


main()