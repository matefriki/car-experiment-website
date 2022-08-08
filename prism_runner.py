from asyncio import base_tasks
from os import system, getcwd
from time import sleep
import os
import json
import sys
import docker


# Ranges for all state variables (inclusive) in order of input
ranges = [
    (1, 300), # path_length
    (50, 100), # person_x
    (0, 15),  # person_y
    (50, 100), # car_x
    (5, 5),   # car_y
    (50, 100), # top_corner_x
    (0, 15),  # top_corner_y
    (50, 100), # bottom_corner_x
    (0, 15)   # bottom_corner_y
]

# Get path to prism directory from config.txt
with open("config.txt", "r") as file:
    prism_path = file.read().strip()

# Split arguments into array of strings
starting_state = [arg for arg in input().split(" ") if arg]

# Ensure correct number of arguments
if len(starting_state) != (len(ranges) + 1):
    sys.exit("Invalid input: incorrect number of args")

# Ensure numerical arguments aren't bigger than reasonable length (10)
if any([len(arg) > 10 for arg in starting_state[1:]]):
    sys.exit("Invalid input: argument too big")

# Ensure all numerical arguments contain only valid characters (positive integers)
if not all([num.isnumeric() for num in starting_state[1:]]):
    sys.exit("Invalid input: not all positive integers")

# Parse numerical arguments to integers
try:
    starting_state[1:] = [int(n) for n in starting_state[1:]]
# Ensure all arguments parse correctly
except Exception as e:
    sys.exit(f"Parse error: {e}")

# Ensure arguments are within desired ranges
def within_range(num, range):
    return num >= range[0] and num <= range[1]
if not all([within_range(arg, ranges[i]) for i, arg in enumerate(starting_state[1:])]):
    sys.exit("Invalid input: argument out of range")

strat_name, path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y = starting_state


# Ensure strat_name is in list of available options
strat_files = {
    "cautious": "dtmc_cautious.pm",
    "normal": "dtmc_normal.pm",
    "agressive": "dtmc_agressive.pm"
}
if strat_name not in strat_files:
    sys.exit("Invalid input: strategy does not exist")

with open(strat_files[strat_name], "r") as file:
    template = file.read()

program = template.format(person_x = person_x, person_y = person_y, car_x = car_x, car_y = car_y, top_corner_x = top_corner_x, top_corner_y = top_corner_y,  bottom_corner_x = bottom_corner_x, bottom_corner_y = bottom_corner_y)
with open("program.pm", "w") as file:
    file.write(program)
sleep(.1)

# writes mdp program to run in storm
with open("mdpgenerated.pm", "r") as file:
    mdptemp = file.read()
mdpprogram = mdptemp.format(person_x = person_x, person_y = person_y, car_x = car_x, car_y = car_y, top_corner_x = top_corner_x, top_corner_y = top_corner_y,  bottom_corner_x = bottom_corner_x, bottom_corner_y = bottom_corner_y)
with open("mdpprogram.pm", "w") as file:
    file.write(mdpprogram)


system("{} program.pm -simpath {} temp/path.txt >/dev/null 2>&1".format(prism_path, path_length)) # >/dev/null 2>&1

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
path = load_path("temp/path.txt")
print(json.dumps(path))

system("python3 trace_convert.py")

client = docker.from_env()

client.containers.run("lposch/tempest-devel-traces:latest", "storm --prism mdpprogram.pm --prop prism_files/mdp_props.props --trace-input trace_input.txt --exportresult mdpprops.json --buildstateval", volumes = {os.getcwd(): {'bind': '/mnt/vol1', 'mode': 'rw'}}, working_dir = "/mnt/vol1", stderr = True)
client.containers.run("lposch/tempest-devel-traces:latest", "storm --prism program.pm --prop prism_files/dtmc_props.props --trace-input trace_input.txt --exportresult dtmcprops.json --buildstateval", volumes = {os.getcwd(): {'bind': '/mnt/vol1', 'mode': 'rw'}}, working_dir = "/mnt/vol1", stderr = True)

system("python3 graph_generator.py")
