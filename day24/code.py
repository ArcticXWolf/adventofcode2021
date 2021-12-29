from __future__ import annotations
import sys, os, re, numpy, itertools, time
import logging
from typing import Dict, List, Tuple, Union

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


def is_int(x: str):
    try:
        int(x)
        return True
    except ValueError:
        return False


def int_if_possible(x: str):
    try:
        return int(x)
    except ValueError:
        return x


def main():
    with open(filename, "r") as f:
        lines = [x.strip() for x in f.readlines()]
        process = Process(lines)

        # part1
        model_number = 99691891979938  # see manual reversing
        number_list = [int(x) for x in list(f"{model_number:014d}")]
        process.run(number_list)
        logging.debug("RESULT %s, input %s", process, model_number)
        if process.z == 0:
            logging.info("Biggest model number is %d", model_number)
        else:
            logging.info("Biggest model number is not %d", model_number)

        # part2
        model_number = 27141191213911  # see manual reversing
        number_list = [int(x) for x in list(f"{model_number:014d}")]
        process.run(number_list)
        logging.debug("RESULT %s, input %s", process, model_number)
        if process.z == 0:
            logging.info("Smallest model number is %d", model_number)
        else:
            logging.info("Smallest model number is not %d", model_number)


class Process:
    REGISTERS = ["w", "x", "y", "z"]
    w: int
    x: int
    y: int
    z: int
    pc: int
    program: List[Tuple[str, List[Union[str, int]]]]
    input: List[int]

    def init_registers(self) -> None:
        self.w = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.pc = 0

    def init_program(self, lines: List[str]) -> None:
        self.program = []
        for line in lines:
            if line == "":
                continue
            splits = line.split()
            opcode = splits.pop(0)
            self.program.append((opcode, [int_if_possible(x) for x in splits]))

    def __init__(self, lines: List[str]) -> None:
        self.init_program(lines)
        self.init_registers()

    def run(self, input: List[int]):
        self.input = input
        self.init_registers()
        for _ in range(len(self.program)):
            self.step()

    def step(self):
        opcode, args = self.program[self.pc]

        callable_opcode = getattr(self, f"op_{opcode}")
        callable_opcode(*args)

        self.pc += 1

    def load_register_or_value(self, arg) -> int:
        if isinstance(arg, str) and arg in self.REGISTERS:
            return getattr(self, arg)
        elif isinstance(arg, int):
            return arg
        raise Exception(f"Arg {arg} not a register nor integer")

    def op_inp(self, arg1):
        if arg1 in self.REGISTERS:
            setattr(self, arg1, self.input.pop(0))
            return
        raise Exception(f"Arg {arg1} not a register")

    def op_add(self, arg1, arg2):
        if arg1 in self.REGISTERS:
            setattr(
                self,
                arg1,
                self.load_register_or_value(arg1) + self.load_register_or_value(arg2),
            )
            return
        raise Exception(f"Arg {arg1} not a register")

    def op_mul(self, arg1, arg2):
        if arg1 in self.REGISTERS:
            setattr(
                self,
                arg1,
                self.load_register_or_value(arg1) * self.load_register_or_value(arg2),
            )
            return
        raise Exception(f"Arg {arg1} not a register")

    def op_div(self, arg1, arg2):
        if arg1 in self.REGISTERS:
            setattr(
                self,
                arg1,
                self.load_register_or_value(arg1) // self.load_register_or_value(arg2),
            )
            return
        raise Exception(f"Arg {arg1} not a register")

    def op_mod(self, arg1, arg2):
        if arg1 in self.REGISTERS:
            setattr(
                self,
                arg1,
                self.load_register_or_value(arg1) % self.load_register_or_value(arg2),
            )
            return
        raise Exception(f"Arg {arg1} not a register")

    def op_eql(self, arg1, arg2):
        if arg1 in self.REGISTERS:
            a = self.load_register_or_value(arg1)
            b = self.load_register_or_value(arg2)
            if a == b:
                setattr(self, arg1, 1)
            else:
                setattr(self, arg1, 0)
            return
        raise Exception(f"Arg {arg1} not a register")

    def __str__(self) -> str:
        return f"Process (w:{self.w} x:{self.x} y:{self.y} z:{self.z} pc:{self.pc} input:{self.input})"


main()