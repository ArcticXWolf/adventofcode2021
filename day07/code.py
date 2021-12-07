from __future__ import annotations
import sys, os
import logging
import statistics, math

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)


def main():
    with open(filename, "r") as f:
        positions = [int(x) for x in f.readline().strip().split(",")]

        # PART 1
        # median should be per definition the position that minimizes the sum of distances
        median = statistics.median_low(positions)
        distances = [abs(median - x) for x in positions]
        logging.info(
            f"Position with lowest fuel requirement with linear fuel consumption: x={median} fuel_total={sum(distances)}"
        )

        # PART 2
        # So, listen.. YES, gradient descent is probably overkill and I probably could have solved this with
        # a closed formula like in part 1 (a mean for the triangular distance metric or something) or by calculating
        # the fuel consumption with the triangular distance for all positions or by just
        # using the mean of positions as estimate and then bruteforcing the real solution from there.
        # HOWEVER:
        # 1. gradient descent works too
        # 2. I always wanted to implement it outside of machine learning for a real usecase
        # 3. it is good for something that otherwise might take a long time computing
        # So no, I wont change that here :P

        # fuel_consumption are triangular numbers, so with n being the distance: n*(n+1)/2
        fuel_consumption = lambda target_position, crab_positions: sum(
            [
                abs(target_position - crab_pos)
                * (abs(target_position - crab_pos) + 1)
                / 2
                for crab_pos in crab_positions
            ]
        )
        # gradient of this distance
        fuel_consumption_gradient = lambda target_position, crab_positions: sum(
            [target_position - crab_pos + 0.5 for crab_pos in crab_positions]
        )
        sign = lambda x: x and (-1 if x < 0 else 1)

        # start gradient descent
        current_pos = math.floor(statistics.mean(positions))  # good first guess
        start_sign_of_gradient = sign(fuel_consumption_gradient(current_pos, positions))
        while (
            sign(fuel_consumption_gradient(current_pos, positions))
            == start_sign_of_gradient
        ):
            gradient = sign(fuel_consumption_gradient(current_pos, positions))
            logging.debug(f"P2 Position {current_pos} Gradient {gradient}")
            current_pos -= gradient

        # adjust for overstepping <- this probably is enough after using the mean as an estimate...
        min_pos = current_pos
        for i in range(-1, 1):
            adjusted_pos = current_pos + i
            if fuel_consumption(adjusted_pos, positions) < fuel_consumption(
                min_pos, positions
            ):
                min_pos = adjusted_pos

        logging.info(
            f"Position with lowest fuel requirement with triangular fuel consumption: x={min_pos} fuel_total={math.floor(fuel_consumption(min_pos, positions))}"
        )


main()