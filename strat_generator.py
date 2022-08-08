import re
import json

# regex used to identify elements to change in original PRISM file
label_reg = re.compile("\/\/\s*{([a-zA-Z_]+)}")
strat_regex = "\[[\w-]+\]"
strategies_label = re.compile(strat_regex)

# generates runnable mdp file
def make_mdp(temp):
    file = open(temp, "r")
    lines = [line.strip() for line in file.readlines()]
    file.close()
    
    for i, line in enumerate(lines):
        label_match = label_reg.search(line)
        # compatible with "".format for changing variables from user input
        if label_match:
            start_ind = line.rfind("init") + 4 if "init" in line else line.rfind("=") + 1
            label = label_match.group(1)
            lines[i] = line[:start_ind] + " {{{}}};".format(label)
        strat_match = strategies_label.search(line)
        # resets car action labels to [], originally set to label for importing strategies
        if strat_match:
            lines[i] = re.sub(strat_regex, "[]", lines[i])

    # rewrites lines into new file
    replaced = '\n'.join(lines)
    with open("temp/mdpgenerated.pm", "w") as f:
        f.write(replaced)

# generates DTMC files for a dictionary and file input
def make_dtmc(temp):
    strats = open('strategy.json')
    strategy = json.load(strats)

    file = open(temp, "r")    
    lines = [line.strip() for line in file.readlines()]
    file.close()
    
    for i, line in enumerate(lines):
        # change file type from mdp to dtmc
        lines[i] = re.sub("mdp", "dtmc", lines[i])
        label_match = label_reg.search(line)
        # compatible with "".format for changing variables from user input
        if label_match:
            start_ind = line.rfind("init") + 4 if "init" in line else line.rfind("=") + 1
            label = label_match.group(1)
            lines[i] = line[:start_ind] + " {{{}}};".format(label)
        # finds strategy labels in PRISM file "[accelerate]..." and adds in corresponding guard
        strat_match = strategies_label.search(line)
        if strat_match:
            for strat in strategy:
                for key in strategy[strat]:
                    if strat_match.group(0) == key: 
                        lines[i] = re.sub(strat_regex, f"[] {strategy[strat][key]}  & ", lines[i]) 
    replaced = '\n'.join(lines)

    for strat in strategy:
        with open(f"temp/dtmc_{strat}.pm", "w") as f:
            f.write(replaced)


def main(prism_file=""):
   

    # If prism file is given (executing normally should be prism_files/mdp.pm), use it. If empty, ask user for it.
    if prism_file == "":
        prism_file = input("Model file to convert to template: ") # use this to give manual input to convert 

    # makes ones mdp file
    make_mdp(prism_file)
    # makes one dtmc file per strategy listed in the json file
    make_dtmc(prism_file)

    # 
    # for strat in strategy:
    #     make_dtmc(strategy[strat], prism_file)

if __name__ == '__main__':
    main("prism_files/mdp.pm")