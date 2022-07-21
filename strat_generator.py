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

def make_dtmc():
    file = open(input("Model file to convert to template: "), "r")
    lines = [line.strip() for line in file.readlines()]
    file.close()

    strats = open('strategy.json')
    strategydict = json.load(strats)
    strategy = strategydict['strategies']

    acc = "accelerate"
    brake = "brake"
    nop = "nop"
    actions = [acc, brake, nop]
    
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
            for strat in strategy:
                for j, nothing in enumerate(strat):
                    if actions[j] == strat_name_label.search(strat_match.group(0)).group(0):
                        lines[i] = re.sub(strat_regex, f"[] {strat[actions[j]]}  & ", lines[i]) 

    replaced = '\n'.join(lines)
    with open("dtmcgenerated.pm", "w") as f:
        f.write(replaced)


make_mdp()
make_dtmc()