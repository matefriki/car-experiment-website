import re
import json

label_reg = re.compile("\/\/\s*{([a-zA-Z_]+)}")
file_label = re.compile("/(mdp)/")
strat_regex = "\[[\w-]+\]"
strategies_label = re.compile(strat_regex)
strat_name_label = re.compile("[\w-]+")


def make_mdp():
    file = open(input("Model file to convert to template: "), "r")
    lines = [line.strip() for line in file.readlines()]
    file.close()
    
    for i, line in enumerate(lines):
        label_match = label_reg.search(line)
        if label_match:
            # print(f"Match: {line}")
            start_ind = line.rfind("init") + 4 if "init" in line else line.rfind("=") + 1
            label = label_match.group(1)
            lines[i] = line[:start_ind] + " {{{}}};".format(label)
        strat_match = strategies_label.search(line)
        if strat_match:
            # print(f"stratmatch: {line}")
            lines[i] = re.sub(strat_regex, "[]", lines[i])

    replaced = '\n'.join(lines)
    with open("mdpgenerated.pm", "w") as f:
        f.write(replaced)


def make_dtmc(dict, temp):
    file = open(temp, "r")    
    lines = [line.strip() for line in file.readlines()]
    file.close()

    print(dict)
    # print(inner)
    # for key in dict:
    #     print(f"key: {key}") # cautious, risky
    #     print(f"dict[key]: {dict[key]}") # the list of acc, br, nop in each "key" = strategy type
    # key = [key for key in dict]
    # change file type from mdp to dtmc
    for i, line in enumerate(lines):
        lines[i] = re.sub("mdp", "dtmc", lines[i])
        label_match = label_reg.search(line)
        if label_match:
            # print(f"Match: {line}")
            start_ind = line.rfind("init") + 4 if "init" in line else line.rfind("=") + 1
            label = label_match.group(1)
            lines[i] = line[:start_ind] + " {{{}}};".format(label)
        strat_match = strategies_label.search(line)
        if strat_match:
            for key in dict:
               
                # print(f"i: {key}")
                # print(f"dict: {dict}")
                # if strat_match.group(0) == key:
                if strat_match.group(0) == key: 
                    print(f"dict[key]: {dict[key]}")
                    lines[i] = re.sub(strat_regex, f"[] {dict[key]}  & ", lines[i]) 
            
    replaced = '\n'.join(lines)
    with open(f"dtmc{strat}.pm", "w") as f:
        f.write(replaced)



# # make_mdp()
strats = open('strategy.json')
strategy = json.load(strats)
for strat in strategy:
# for i in range(1):
    make_dtmc(strategy[strat], "test.pm")