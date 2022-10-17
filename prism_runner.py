from asyncio import base_tasks
from os import system, getcwd
import re
from time import sleep
import os
import json
import sys
import docker
import pandas as pd, numpy as np
import strat_generator
import trace_convert
import graph_generator
import pickle


# Ranges for all state variables (inclusive) in order of input
ranges = [
    (1, 300), # path_length
    (25, 75), # person_x
    (0, 15),  # person_y
    (25, 75), # car_x
    (5, 5),   # car_y
    (25, 75), # top_corner_x
    (0, 15),  # top_corner_y
    (25, 75), # bottom_corner_x
    (0, 15)   # bottom_corner_y
]

# Get path to prism directory from config.txt
with open("config.txt", "r") as file:
    prism_path = file.read().strip()

# Split arguments into array of strings
starting_state = [arg for arg in input().split(" ") if arg]
# starting_state = [arg for arg in sys.argv[1:] if arg]
# print(starting_state)

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

strategies, path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y = starting_state

# Ensure strat_name is in list of available options

strat_files = {
    "cautious": "temp/dtmc_cautious.pm",
    "normal": "temp/dtmc_normal.pm",
    "agressive": "temp/dtmc_agressive.pm",
    "car1":"temp/dtmc_car1.pm",
    "car2":"temp/dtmc_car2.pm",
    "car3":"temp/dtmc_car3.pm",
    "car4":"temp/dtmc_car4.pm"
}

strat_list = strategies.split(",")
if len(strat_list) == 0:
    sys.exit("Invalid input: no strategies provided")

for name in strat_list:
    if name not in strat_files:
        sys.exit("Invalid input: strategy does not exist")

# check if mpggenerated is there. If not, creates it in temp folder, along with dtmc files
path_to_generated_mdp = "temp/mdpgenerated.pm"
if not os.path.exists(path_to_generated_mdp):
    strat_generator.main("prism_files/mdp.pm")

with open(strat_files[strat_list[0]], "r") as file:
    template = file.read()

program = template.format(person_x = person_x, person_y = person_y, car_x = car_x, car_y = car_y, top_corner_x = top_corner_x, top_corner_y = top_corner_y,  bottom_corner_x = bottom_corner_x, bottom_corner_y = bottom_corner_y)
with open("program.pm", "w") as file:
    file.write(program)
sleep(.1)

# writes mdp program to run in storm, if file did not exist before, creates it from mpd.pm
with open(path_to_generated_mdp, "r") as file:
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

# system("python3 trace_convert.py")
ordered_list_of_states = trace_convert.main()

client = docker.from_env()

client.containers.run("lposch/tempest-devel-traces:latest", "storm --prism mdpprogram.pm --prop prism_files/mdp_props.props --trace-input trace_input.txt --exportresult mdpprops.json --buildstateval", volumes = {os.getcwd(): {'bind': '/mnt/vol1', 'mode': 'rw'}}, working_dir = "/mnt/vol1", stderr = True)
client.containers.run("lposch/tempest-devel-traces:latest", "storm --prism program.pm --prop prism_files/dtmc_props.props --trace-input trace_input.txt --exportresult dtmcprops.json --buildstateval", volumes = {os.getcwd(): {'bind': '/mnt/vol1', 'mode': 'rw'}}, working_dir = "/mnt/vol1", stderr = True)

names = ['dtmc','mdp','1mdp']
pminmax = []*len(names)
for name in names:
    with open(f'{name}props.json',) as file:
            trace = json.load(file)
    if not trace:
        sys.exit("JSON load error: can't load props (likely trace too short)")
    probs = []*len(trace)
    file = open('trace', 'wb')
    pickle.dump(trace, file)
    file.close()
    file = open('ordered_list_of_states', 'wb')
    pickle.dump(ordered_list_of_states, file)
    file.close()
    # check for repeated states
    number_of_repeated_states = 0
    for i in range(1,len(ordered_list_of_states)):
        if ordered_list_of_states[i] == ordered_list_of_states[i-1]:
            number_of_repeated_states += 1
    if number_of_repeated_states > 0:
        print(f"There were {number_of_repeated_states} repeated_states.\n")
    # check for trivial states
    for i in range(len(ordered_list_of_states)):
        found = False
        for j in range(len(trace)):
            if trace[j]['s'] == ordered_list_of_states[i]:
                found = True
        if not found:
            laststate = {'s':ordered_list_of_states[i], 'v':1}
            trace.append(laststate)
            print('Added last state')


    assert len(ordered_list_of_states) == len(trace)+number_of_repeated_states, 'Arrays of different size'
    for i in range(len(ordered_list_of_states)):
        for j in range(len(trace)):
            if ordered_list_of_states[i] == trace[j]['s']:
                probs.append(trace[j]['v'])
    pminmax.append(probs)

columns = ['Pmin', 'Pmax', 'P', 'Rmin', 'Rmax', 'R']
df1 = pd.DataFrame(0, index=np.arange(len(ordered_list_of_states)), columns=columns)
for i in df1.index:
        p = pminmax[0][i]
        r = 0  # r is maintained for backwards compatibility, not computed anymore
        pmin = pminmax[2][i]
        pmax = pminmax[1][i]
        rmin = 0
        # rmax = getProbs(Rmaxfile)[i]
        rmax = 0 # r is maintained for backwards compatibility, not computed anymore
        df1.loc[i,:] = [pmin, pmax, p, rmin, rmax, r]
# fill df with pmin pmax
# for strat in set_of_strategies:
#     make the program file program.pm
#     client.containers.run("lposch/tempest-devel-traces:latest", "storm --prism program.pm --prop prism_files/dtmc_props.props --trace-input trace_input.txt --exportresult dtmcprops.json --buildstateval", volumes = {os.getcwd(): {'bind': '/mnt/vol1', 'mode': 'rw'}}, working_dir = "/mnt/vol1", stderr = True)    
#     fill_df with p of the strategy


graph_generator.main(df1, strat_list[0])
# system("python3 graph_generator.py")