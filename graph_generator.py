import pandas as pd
import numpy as np
from matplotlib import rc
from matplotlib import pyplot as plt
import json

def getProbs(file):
    keys = []
    for key in file:
        keys.append(key['v'])
    # print(len(keys))
    return keys

def firstPlot(df, states, state_ticks, state_labels, idx=0):    
    # set up the plots
    fig, axs1 = plt.subplots(figsize = (7, 5))
    axs1.set_xlim(0,df.shape[0])
    for spine in ['right', 'top']:
        axs1.spines[spine].set_visible(False)

    # plotting data
    axs1.fill_between(states, df['Pmin'], df['Pmax'], color = '#DBDBDB')
    axs1.plot(states, df['Pmin'], color = '#1a4314', marker = 'o', label = "Pmin", zorder=10, clip_on=False)
    axs1.plot(states, df['Pmax'], color = '#8d0000', marker = 'o', label = "Pmax", zorder=10, clip_on=False)

    # make a P line for each strategy chosen by user, new color, df will be new, new label
    axs1.plot(states, df['P'], color = '#ca06b8', marker = 'o', label = "P", zorder=10, clip_on=False)
    axs1.vlines(idx,0,1)
    
    # labelling plot
    axs1.legend()
    axs1.set_xlabel('States')
    plt.xticks(state_ticks, state_labels)
    axs1.set_ylabel('Probability')
    plt.yticks([0, 0.5, 1.0], ['0','0.5', '1.0'])
    axs1.set_title('le titre')
    axs1.plot(1, 0, ">k", transform=axs1.get_yaxis_transform(), clip_on=False)
    
    # plt.tight_layout()
    axs1.margins(0)
    plt.savefig("temp/graph_left.png")

def secondPlot(df, states, state_ticks, state_labels, idx=0):    
    # set up the plots
    fig, axs2 = plt.subplots(figsize = (7, 5))
    axs2.set_xlim(0, df.shape[0])
    for spine in ['right', 'top']:
        axs2.spines[spine].set_visible(False)

    # making data for the plots
    ro1 = []
    roDiff = []
    ro1 = (df['P'] - df['Pmin'])/(df['Pmax'] - df['Pmin'])
    roDiff = df['Pmax'] - df['Pmin']
    roDiffWidth = 0.25

    # plotting the data
    axs2.plot(states, ro1, color = '#ca06b8', marker = 'o', label = "rho1", zorder=10, clip_on=False)
    axs2.axhline(y = ro1.mean(), color = '#ca06b8', linestyle = '--', label = "rho1 Mean")
    axs2.bar(states, roDiff, roDiffWidth, color = '#DBDBDB', edgecolor = '#BFBFBF')
    axs2.axvline(x = idx)
    axs2.legend()

    # labelling the plot
    axs2.set_xlabel('States')
    plt.xticks(state_ticks, state_labels)
    axs2.set_ylabel('Probability')
    plt.yticks([0,0.5, 1.0], ['0','0.5', '1.0'])
    axs2.plot(1, 0, ">k", transform=axs2.get_yaxis_transform(), clip_on=False)
    axs2.set_title('le titre')
        
    # axs2.margins(0)
    plt.savefig("temp/graph_right.png")

def main(df1):
    df1.to_csv("temp/data.csv")
    # only use data until Pmax-Pmix < eps (data after this is useless)
    idx = df1.index[-1]
    eps = 0.01
    rodiff11 = df1['Pmax'] - df1['Pmin']

    while idx > 0:
        if np.abs(rodiff11[idx]) < eps:
            idx = idx -1 
        else:
            break
    # df = df1[0:idx]
    if idx + 3 < df1.index[-1]:
        df = df1[0:idx+3]
    else:
        df = df1 
    # both graphs will plot to the same state tick
    state_labels = []
    states = []
    state_ticks = []
    for i in range(df.shape[0]):
        states.append(i)
    for i in range(df.shape[0]):
        if i*5 < df.shape[0] -1:
            state_labels.append(f"s{5*i + 1}")
            state_ticks.append(5*i + 1)

    # plot styling
    plt.rcParams.update({'axes.labelsize' : 18, 'axes.titlesize': 18, 'font.family': 'serif'})

    firstPlot(df, states, state_ticks, state_labels, idx)
    secondPlot(df, states, state_ticks, state_labels, idx)

if __name__ == "__main__":
    df = pd.read_csv('temp/data.csv')
    main(df)