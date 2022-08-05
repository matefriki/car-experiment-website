import re
import json

file = open("path.txt", "r")
lines = [line.strip() for line in file.readlines()]
file.close()

label_dash = re.compile("-")
label_ped = re.compile("Pedestrian")
label_car = re.compile("Car")

    # make each array item into sep array
path_lines = [item.split(" ") for item in lines]
labels = path_lines[0]
path_lines = path_lines[1:]
dict = {}
for i, label in enumerate(labels):
    dict[label] = [row[i] for row in path_lines]

dict.pop('action')
dict.pop('step')
with open("dictdict.json", "w") as jsonfile:
    json.dump(dict, jsonfile)

arr = []
length = len(dict['turn'])
for j, line in enumerate(lines):
    label_match1 = label_ped.search(line)
    label_match2 = label_car.search(line)
    if (label_match1 == None) | (label_match2 == None):
        lines[j] = ""
    if ((label_match1 != None) | (label_match2 != None)) & (j <= length):
        if [f"{key}={dict[key][j-1]}" for key in dict][0] == 'turn=0':
            arr.append([f"{key}={dict[key][j-1]}" for key in dict])


for i,input in enumerate(arr):
    for j,str in enumerate(input):
        lines[i] += f"{str}"
        if j != len(arr[i]) - 1:
            lines[i] += " & "


replaced = '\n'.join(lines)
with open("trace_input.txt", "w") as f:
    f.write(replaced)