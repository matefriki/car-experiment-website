import re
import json

# regex used to identify elements to change in original PRISM file
label_reg = re.compile("\/\/\s*{([a-zA-Z_]+)}")
strat_regex = "\[[\w-]+\]"
strategies_label = re.compile(strat_regex)

def nice_parenthesis(instring):
    result = ""
    currenttab = 0
    for i in instring:
        
        if i == '(':
            currenttab += 1
            result += "(\n"
            for j in range(currenttab):
                result += "\t"
        elif i == ')':
            currenttab -= 1
            result += "\n"
            for j in range(currenttab):
                result += "\t"
            result += ")"
        elif (i != ' ') and (i != '\n'):
            result +=i
    return result

# generates runnable mdp file
def make_mdp(temp, hesitant_pedestrian):
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
        # hesitant pedestrian part: if not hesitant, danger formulas set to false
        if not hesitant_pedestrian:
            if "formula danger_to_cross" in line:
                lines[i] = "formula danger_to_cross = false;"
            if "formula danger_to_stay" in line:
                lines[i] = "formula danger_to_stay = false;"

    # rewrites lines into new file
    replaced = '\n'.join(lines)
    with open("temp/mdpgenerated.pm", "w") as f:
        f.write(replaced)

# generates DTMC files for a dictionary and file input
def make_dtmc(temp, use_visibility=False, hesitant_pedestrian=False):
    strats = open('strategy.json')
    strategy = json.load(strats) ## this is a dict, keys are names of strategies

    if not use_visibility:
        for keystrat in strategy.keys():
            for keyaction in strategy[keystrat].keys():
                strategy[keystrat][keyaction] = strategy[keystrat][keyaction].replace(' ', '')
                strategy[keystrat][keyaction] = strategy[keystrat][keyaction].replace('seen_ped=0', 'false')
                strategy[keystrat][keyaction] = strategy[keystrat][keyaction].replace('seen_ped=1', 'true')
                strategy[keystrat][keyaction] = strategy[keystrat][keyaction].replace('visibility=0', 'false')
                strategy[keystrat][keyaction] = strategy[keystrat][keyaction].replace('visibility=1', 'true')

    for strat in strategy:

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
            # hesitant pedestrian part: if not hesitant, danger formulas set to false
            if not hesitant_pedestrian:
                if "formula danger_to_cross" in line:
                    lines[i] = "formula danger_to_cross = false;"
                if "formula danger_to_stay" in line:
                    lines[i] = "formula danger_to_stay = false;"
            # finds strategy labels in PRISM file "[accelerate]..." and adds in corresponding guard
            strat_match = strategies_label.search(line)
            if strat_match:
                for key in strategy[strat]:
                    if strat_match.group(0) == key: 
                        lines[i] = re.sub(strat_regex, f"[] {nice_parenthesis(strategy[strat][key])}  & ", lines[i]) 
        replaced = '\n'.join(lines)
        with open(f"temp/dtmc_{strat}.pm", "w") as f:
            f.write(replaced)
        


def main(prism_file="", use_visibility=False, hesitant_pedestrian=False):
   

    # If prism file is given (executing normally should be prism_files/mdp.pm), use it. If empty, ask user for it.
    if prism_file == "":
        prism_file = input("Model file to convert to template: ") # use this to give manual input to convert 

    # makes ones mdp file
    make_mdp(prism_file, hesitant_pedestrian = hesitant_pedestrian)
    # makes one dtmc file per strategy listed in the json file
    make_dtmc(prism_file, use_visibility = use_visibility, hesitant_pedestrian = hesitant_pedestrian)

    # 
    # for strat in strategy:
    #     make_dtmc(strategy[strat], prism_file)

if __name__ == '__main__':
    main("prism_files/mdp.pm")