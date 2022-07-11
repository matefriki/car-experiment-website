import re

file = open(input("Model file to convert to template: "), "r")
lines = [line.strip() for line in file.readlines()]
file.close()

label_reg = re.compile("\/\/\s*{([a-zA-Z_]+)}")


for i, line in enumerate(lines):
    label_match = label_reg.search(line)
    if label_match:
        print(f"Match: {line}")
        start_ind = line.rfind("init") + 4 if "init" in line else line.rfind("=") + 1
        label = label_match.group(1)
        lines[i] = line[:start_ind] + " {{{}}};".format(label)

replaced = '\n'.join(lines)
with open("generated.pm", "w") as f:
    f.write(replaced)