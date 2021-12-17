from __future__ import annotations
import struct
import sys, os, copy
import logging
from typing import Deque, Dict, Generator, List, Set, Tuple, Union
import itertools, textwrap, math

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


def get_bitlist(input: bytes) -> List[int]:
    return [b >> (7 - i) & 1 for b in input for i in range(8)]


def pack_bitlist(input: List[int]) -> int:
    return sum(b << (len(input) - i - 1) for i, b in enumerate(input))


class BasePacket:
    version: int
    type: int
    length: int

    @classmethod
    def parse(cls, input: List[int]) -> BasePacket:
        type = pack_bitlist(input[3:6])
        if type == 0:
            return SumPacket(input)
        elif type == 1:
            return ProductPacket(input)
        elif type == 2:
            return MinimumPacket(input)
        elif type == 3:
            return MaximumPacket(input)
        elif type == 4:
            return LiteralValuePacket(input)
        elif type == 5:
            return GreaterThanPacket(input)
        elif type == 6:
            return LessThanPacket(input)
        elif type == 7:
            return EqualToPacket(input)
        return OperatorPacket(input)

    def __init__(self, input: List[int], length: int = 0) -> None:
        self.version = pack_bitlist(input[0:3])
        self.type = pack_bitlist(input[3:6])
        self.length = length + 6

    def result(self) -> int:
        return 0

    def version_sum(self) -> int:
        return self.version

    def __str__(self) -> str:
        return f"BasePacket(v={self.version}, t={self.type})"


class LiteralValuePacket(BasePacket):
    value: int

    def __init__(self, input: List[int]) -> None:
        bits = input[6:]
        bitgroups = itertools.zip_longest(*(iter(bits),) * 5)
        self.value = 0
        length = 0
        for bitgroup in bitgroups:
            length += 5
            self.value = (self.value << 4) | pack_bitlist(bitgroup[1:])
            if bitgroup[0] == 0:
                break

        super().__init__(input, length)

    def result(self) -> int:
        return self.value

    def __str__(self) -> str:
        return f"LVPacket(v={self.version}, t={self.type}, r={self.result()})"


class OperatorPacket(BasePacket):
    is_subpacket_length_by_count: bool
    subpacket_length: int
    subpackets: List[BasePacket]

    def __init__(self, input: List[int]) -> None:
        self.is_subpacket_length_by_count = input[6] == 1
        self.subpackets = []
        total_length = 1

        if self.is_subpacket_length_by_count:
            self.subpacket_length = pack_bitlist(input[7:18])
            total_length += 11
            current_index = 18
            for _ in range(self.subpacket_length):
                packet = BasePacket.parse(input[current_index:])
                total_length += packet.length
                current_index += packet.length
                self.subpackets.append(packet)
        else:
            self.subpacket_length = pack_bitlist(input[7:22])
            total_length += 15
            current_index = 22
            while current_index - 22 < self.subpacket_length:
                packet = BasePacket.parse(input[current_index:])
                total_length += packet.length
                current_index += packet.length
                self.subpackets.append(packet)

        super().__init__(input, total_length)

    def result(self) -> int:
        return 0

    def version_sum(self) -> int:
        return super().version_sum() + sum(
            subpacket.version_sum() for subpacket in self.subpackets
        )

    def __str__(self) -> str:
        subpacket_text = "\n".join(str(x) for x in self.subpackets)
        return f"{self.__class__.__name__}(v={self.version}, vs={self.version_sum()}, t={self.type}, lt={self.is_subpacket_length_by_count}, l={self.subpacket_length}, r={self.result()}):\n{textwrap.indent(subpacket_text,'    ')}"


class SumPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)

    def result(self) -> int:
        return sum(subpacket.result() for subpacket in self.subpackets)


class ProductPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)

    def result(self) -> int:
        return math.prod(subpacket.result() for subpacket in self.subpackets)


class MinimumPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)

    def result(self) -> int:
        return min(subpacket.result() for subpacket in self.subpackets)


class MaximumPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)

    def result(self) -> int:
        return max(subpacket.result() for subpacket in self.subpackets)


class GreaterThanPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)
        if len(self.subpackets) != 2:
            raise Exception("Comparison packet has not exactly two subpackets")

    def result(self) -> int:
        if self.subpackets[0].result() > self.subpackets[1].result():
            return 1
        return 0


class LessThanPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)
        if len(self.subpackets) != 2:
            raise Exception("Comparison packet has not exactly two subpackets")

    def result(self) -> int:
        if self.subpackets[0].result() < self.subpackets[1].result():
            return 1
        return 0


class EqualToPacket(OperatorPacket):
    def __init__(self, input: List[int]) -> None:
        super().__init__(input)
        if len(self.subpackets) != 2:
            raise Exception("Comparison packet has not exactly two subpackets")

    def result(self) -> int:
        if self.subpackets[0].result() == self.subpackets[1].result():
            return 1
        return 0


def main():
    with open(filename, "r") as f:
        for input in f.readlines():
            packet = BasePacket.parse(get_bitlist(bytes.fromhex(input.strip())))
            logging.info("%s", packet)


main()