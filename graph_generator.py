import pandas as pd
import numpy as np
from matplotlib import rc
from matplotlib import pyplot as plt
import json

COLORBOX = ['#ca06b8', '#ca9236', '#5132c7', '#3bf48c', '#bed092']

def getProbs(file):
    keys = []
    for key in file:
        keys.append(key['v'])
    # print(len(keys))
    return keys

def firstPlot(dfarray, states, state_ticks, state_labels, idx=0, strat_names=['strategy']):    
    # set up the plots
    fig, axs1 = plt.subplots(figsize = (7, 5))
    axs1.set_xlim(0,dfarray[0].shape[0])
    for spine in ['right', 'top']:
        axs1.spines[spine].set_visible(False)

    # plotting data
    axs1.fill_between(states, dfarray[0]['Pmin'], dfarray[0]['Pmax'], color = '#DBDBDB')
    axs1.plot(states, dfarray[0]['Pmin'], color = '#1a4314', marker = 'o', label = "Pmin", zorder=10, clip_on=False, alpha=0.5)
    axs1.plot(states, dfarray[0]['Pmax'], color = '#8d0000', marker = 'o', label = "Pmax", zorder=10, clip_on=False, alpha=0.5)

    # make a P line for each strategy chosen by user, new color, df will be new, new label
    for i in range(len(dfarray)):
        df = dfarray[i]
        strat_name = strat_names[i]
        axs1.plot(states, df['P'], color = COLORBOX[i%len(COLORBOX)], marker = 'o', label = strat_name, zorder=10, clip_on=False, alpha=0.5)


    axs1.vlines(idx,0,1)
    
    # labelling plot
    axs1.legend()
    axs1.set_xlabel('States')
    plt.xticks(state_ticks, state_labels)
    axs1.set_ylabel('Probability')
    plt.yticks([0, 0.5, 1.0], ['0','0.5', '1.0'])
    axs1.set_title('Raw probabilities')
    axs1.plot(1, 0, ">k", transform=axs1.get_yaxis_transform(), clip_on=False)
    
    # plt.tight_layout()
    axs1.margins(0)
    plt.savefig("temp/graph_left.png")

def secondPlot(dfarray, states, state_ticks, state_labels, idx=0, strat_names=['strategy']):    
    # set up the plots
    fig, axs2 = plt.subplots(figsize = (7, 5))
    axs2.set_xlim(0, dfarray[0].shape[0])
    for spine in ['right', 'top']:
        axs2.spines[spine].set_visible(False)
    roDiff = []
    roDiff = dfarray[0]['Pmax'] - dfarray[0]['Pmin']
    roDiffWidth = 0.25

    # making data for the plots
    for i in range(len(dfarray)):
        df = dfarray[i]
        strat_name = strat_names[i]
        ro1 = []
        ro1 = (df['P'] - df['Pmin'])/(df['Pmax'] - df['Pmin'])
        axs2.plot(states, ro1, color = COLORBOX[i%len(COLORBOX)], marker = 'o', label = f"rho {strat_name}", zorder=10, clip_on=False)
        axs2.axhline(y = ro1.mean(), color = COLORBOX[i%len(COLORBOX)], linestyle = '--', label = "rho1 Mean")

    # plotting the data
    axs2.bar(states, roDiff, roDiffWidth, color = '#DBDBDB', edgecolor = '#BFBFBF')
    axs2.axvline(x = idx)
    axs2.legend()

    # labelling the plot
    axs2.set_xlabel('States')
    plt.xticks(state_ticks, state_labels)
    axs2.set_ylabel('Probability')
    plt.yticks([0,0.5, 1.0], ['0','0.5', '1.0'])
    axs2.plot(1, 0, ">k", transform=axs2.get_yaxis_transform(), clip_on=False)
    axs2.set_title('Relative intention')
        
    # axs2.margins(0)
    plt.savefig("temp/graph_right.png")

def main(df1array, strat_names = ['strategy']):
    assert(len(df1array) == len(strat_names))
    for i in range(len(strat_names)):
        df1array[i].to_csv(f"temp/data_{strat_names[i]}.csv")
    # only use data until Pmax-Pmix < eps (data after this is useless)
    dfarray = []
    for i in range(len(df1array)):
        df1 = df1array[i]
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
        dfarray.append(df)
    
    # both graphs will plot to the same state tick
    state_labels = []
    states = []
    state_ticks = []
    for i in range(dfarray[0].shape[0]):
        states.append(i)
    for i in range(dfarray[0].shape[0]):
        if i*5 < dfarray[0].shape[0] -1:
            state_labels.append(f"s{5*i + 1}")
            state_ticks.append(5*i + 1)

    # plot styling
    plt.rcParams.update({'axes.labelsize' : 18, 'axes.titlesize': 18, 'font.family': 'serif'})

    firstPlot(dfarray, states, state_ticks, state_labels, idx, strat_names)
    secondPlot(dfarray, states, state_ticks, state_labels, idx, strat_names)

if __name__ == "__main__":
    df = pd.read_csv('temp/data.csv')
    main(df)