import pandas as pd
import json
from tqdm import tqdm
import time
import os
import subprocess


def main():
    slippery_ranges = [(40, 50), (30,55)] # range of street x where car is slippery (min, max)
    slippery_factors = [1,1.5,2,2.5] # between 1 and inf, inf max slipperyness
    hesitant_factors = [0.3, 0.6, 1] # between 0 and 1, 0 max hesitancy
    folder_to_save = 'path_crash10'
    os.system(f"mkdir {folder_to_save}")

    all_counterfactuals_array = []
    for slippery_range in slippery_ranges:
        for slippery_factor in slippery_factors:
            for hesitant_factor in hesitant_factors:
                all_counterfactuals_array.append({'slippery_range':slippery_range,
                                                   'slippery_factor':slippery_factor,
                                                   'hesitant_factor':hesitant_factor})
    
    for cf in tqdm(all_counterfactuals_array):
        with open('params.json','r') as fp:
            params = json.load(fp)
        params["slippery_range"] = f"(car_x > {cf['slippery_range'][0]}) & (car_x < {cf['slippery_range'][1]})"
        params["slippery_factor"] = cf['slippery_factor']
        params["hesitant_factor"] = cf['hesitant_factor']
        with open('params.json', 'w') as fp:
            json.dump(params,fp,indent=2)
        outputfile = 'prism_output_file.txt'
        with open(outputfile, 'w') as foo:
            with open('inputtotest.txt', 'r') as fin:
                p = subprocess.Popen(['python3', 'prism_runner.py'], stdin=fin, stdout=foo, shell=False)
                try:
                    p.wait(100)
                except:
                    p.kill()
                    print(f"Had to kill prism runner after with 100 seconds with \n")
                    print(params)
                    print('\n---------\n')
        graphs_added_name = f"{cf['slippery_range'][0]}_{cf['slippery_range'][1]}_{cf['slippery_factor']}_{cf['hesitant_factor']}"
        os.system(f"cp temp/graph_left.png {folder_to_save}/{graphs_added_name}_graph_left.png")
        os.system(f"cp temp/graph_right.png {folder_to_save}/{graphs_added_name}_graph_right.png")

if __name__ == "__main__":
    main()