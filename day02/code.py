import sys

commands = []
with open(sys.argv[1], "r") as f:
    for line in f.readlines():
        command, value = line.split(" ")[0], line.split(" ")[1].strip()
        commands.append((command, int(value)))

horizontal_position = 0
depth = 0

for command, value in commands:
    if command == "forward":
        horizontal_position += value
    elif command == "down":
        depth += value
    elif command == "up":
        depth -= value
    else:
        print(f"unknown command {command} {value}")

print(
    f"01: HPos: {horizontal_position}, Depth: {depth}, Mul: {horizontal_position*depth}"
)

horizontal_position = 0
depth = 0
aim = 0
for command, value in commands:
    if command == "forward":
        horizontal_position += value
        depth += aim * value
    elif command == "down":
        aim += value
    elif command == "up":
        aim -= value
    else:
        print(f"unknown command {command} {value}")

print(
    f"02: HPos: {horizontal_position}, Depth: {depth}, Aim: {aim}, Mul: {horizontal_position*depth}"
)