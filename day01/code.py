import sys

depths = []
with open(sys.argv[1], "r") as f:
    depths = [int(x) for x in f.readlines()]

windows = [0 for i in range(len(depths) - 2)]
for index, current_depth in enumerate(depths):
    if index < len(windows):
        windows[index] += current_depth
    if index - 1 >= 0 and index - 1 < len(windows):
        windows[index - 1] += current_depth
    if index - 2 >= 0:
        windows[index - 2] += current_depth

last_depth = 100000000000000000
increments = 0
for current_depth in depths:
    if current_depth > last_depth:
        increments += 1
    last_depth = current_depth

print(f"Increments: {increments}")

last_depth = 100000000000000000
increments = 0
for current_depth in windows:
    if current_depth > last_depth:
        increments += 1
    last_depth = current_depth

print(f"Window increments: {increments}")