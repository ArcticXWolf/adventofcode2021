from __future__ import annotations
import sys, os
import logging
import statistics, math
from typing import Dict, List, Set

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)


class Decoder:
    raw_digit_characters: List[Set[str]]
    raw_output_characters: List[Set[str]]
    digit_word_map: Dict[int, Set[str]]

    def __init__(self, line: str) -> None:
        self.raw_digit_characters = []
        self.raw_output_characters = []
        self.digit_word_map = {i: "" for i in range(10)}

        left_side, right_side = (
            line.split("|")[0].strip(),
            line.split("|")[1].strip(),
        )

        for word in left_side.split():
            self.raw_digit_characters.append(set(word))

        for word in right_side.split():
            self.raw_output_characters.append(set(word))

    def count_1478s_in_output(self) -> int:
        counter = 0
        for word in self.raw_output_characters:
            if len(word) in [2, 3, 4, 7]:
                counter += 1
        return counter

    def _identify_numbers(self) -> None:
        words_left = self.raw_digit_characters
        # by count
        self.digit_word_map[1] = next(x for x in words_left if len(x) == 2)
        words_left.remove(self.digit_word_map[1])
        self.digit_word_map[4] = next(x for x in words_left if len(x) == 4)
        words_left.remove(self.digit_word_map[4])
        self.digit_word_map[7] = next(x for x in words_left if len(x) == 3)
        words_left.remove(self.digit_word_map[7])
        self.digit_word_map[8] = next(x for x in words_left if len(x) == 7)
        words_left.remove(self.digit_word_map[8])

        # by count and containment rules
        # 6 is the only number which is length 6 and does not contain all segments of 1
        self.digit_word_map[6] = next(
            x
            for x in words_left
            if len(x) == 6 and not self.digit_word_map[1].issubset(x)
        )
        words_left.remove(self.digit_word_map[6])

        # 0 is the only number left which is length 6 and does not contain all segments of 4
        self.digit_word_map[0] = next(
            x
            for x in words_left
            if len(x) == 6 and not self.digit_word_map[4].issubset(x)
        )
        words_left.remove(self.digit_word_map[0])

        # 9 is the only number left which is length 6 (and does contain all segments of 4)
        self.digit_word_map[9] = next(
            x for x in words_left if len(x) == 6 and self.digit_word_map[4].issubset(x)
        )
        words_left.remove(self.digit_word_map[9])

        # 3 is the only number left which is length 5 and does contain all segments of 1
        self.digit_word_map[3] = next(
            x for x in words_left if len(x) == 5 and self.digit_word_map[1].issubset(x)
        )
        words_left.remove(self.digit_word_map[3])

        # 5 is the only number left which is length 5 and which segment difference to the segments of 6 is 1
        self.digit_word_map[5] = next(
            x
            for x in words_left
            if len(x) == 5
            and sum([elem not in x for elem in self.digit_word_map[6]]) == 1
        )
        words_left.remove(self.digit_word_map[5])

        # 2 is the only number left now
        self.digit_word_map[2] = words_left.pop()

    def decode_output(self) -> List[int]:
        self._identify_numbers()
        result = []
        for output_code in self.raw_output_characters:
            result.append(
                next(i for i, x in self.digit_word_map.items() if x == output_code)
            )
        return result


def main():
    with open(filename, "r") as f:
        # parse input
        decodings = [Decoder(line.strip()) for line in f.readlines()]

        # part1
        logging.info(
            f"Amount of 1478 in output digits: {sum([d.count_1478s_in_output() for d in decodings])}"
        )

        # part2
        sum_total = 0
        for index, decoder in enumerate(decodings):
            result = decoder.decode_output()
            mappings = {i: "".join(word) for i, word in decoder.digit_word_map.items()}
            logging.debug(f"{index} Identified number mappings: {mappings}")
            logging.debug(f"{index} Decoded output numbers: {result}")
            sum_total += int("".join([str(x) for x in result]))

        logging.info(f"Sum of all decoded output digits: {sum_total}")


main()