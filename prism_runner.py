from asyncio import base_tasks
from os import system
from time import sleep
import json
import sys

# Ranges for all state variables (inclusive) in order of input
ranges = [
    (1, 300), # path_length
    (0, 100), # person_x
    (0, 15),  # person_y
    (0, 100), # car_x
    (0, 15),  # car_y
    (0, 100), # top_corner_x
    (0, 15),  # top_corner_y
    (0, 100), # bottom_corner_x
    (0, 15)   # bottom_corner_y
]

# Get path to prism directory from config.txt
with open("config.txt", "r") as file:
    prism_path = file.read().strip()

# Split arguments into array of strings
starting_state = [arg for arg in input().split(" ") if arg]

# Ensure correct number of arguments
if len(starting_state) != 9:
    sys.exit("Invalid input: incorrect number of args")

# Ensure arguments aren't bigger than reasonable length (10)
if any([len(arg) > 10 for arg in starting_state]):
    sys.exit("Invalid input: argument too big")

# Ensure all arguments contain only valid characters (positive integers)
if not all([num.isnumeric() for num in starting_state]):
    sys.exit("Invalid input: not all positive integers")

# Parse arguments to integers
try:
    starting_state = [int(n) for n in starting_state]
# Ensure all arguments parse correctly
except Exception as e:
    sys.exit(f"Parse error: {e}")

# Ensure arguments are within desired ranges
def within_range(num, range):
    return num >= range[0] and num <= range[1]
if not all([within_range(arg, ranges[i]) for i, arg in enumerate(starting_state)]):
    sys.exit("Invalid input: argument out of range")

path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y = starting_state

with open("template.pm", "r") as file:
    template = file.read()

program = template.format(person_x = person_x, person_y = person_y, car_x = car_x, car_y = car_y, top_corner_x = top_corner_x, top_corner_y = top_corner_y,  bottom_corner_x = bottom_corner_x, bottom_corner_y = bottom_corner_y)
with open("program.pm", "w") as file:
    file.write(program)
sleep(.1)

system("{} program.pm -simpath {} path.txt >/dev/null 2>&1".format(prism_path, path_length)) # >/dev/null 2>&1

def load_path(file_name):
    file = open(file_name, "r")
    path_lines = [x.strip() for x in file.readlines()]
    file.close()

    # make each array item into sep array
    path_lines = [item.split(" ") for item in path_lines]
    labels = path_lines[0]
    path_lines = path_lines[1:]

    path = {}
    for i, label in enumerate(labels):
        path[label] = [row[i] for row in path_lines]

    return path

sleep(.1)
path = load_path("path.txt")
print(json.dumps(path))