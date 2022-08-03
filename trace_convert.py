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
path = {}
for i, label in enumerate(labels):
    path[label] = [row[i] for row in path_lines]
path.pop('action')
path.pop('step')
with open("pathdict.json", "w") as jsonfile:
    json.dump(path, jsonfile)

arr = []
for i, line in enumerate(lines):
    # print(i)
    label_match1 = label_ped.search(line)
    label_match2 = label_car.search(line)

    if (label_match1 == None) | (label_match2 == None):
        lines[i] = ""

    if ((label_match1 != None) | (label_match2 != None)) & (i <= 101):

        arr.append([f"{key}={path[key][i-1]}" for key in path])

for i,input in enumerate(arr):
    # stringbean = ""
    for j,str in enumerate(input):
        lines[i] += f"{str}"
        if j != len(arr[i]) - 1:
            lines[i] += " & "
# print(stringbean)


replaced = '\n'.join(lines)
with open("trace_input.txt", "w") as f:
    f.write(replaced)