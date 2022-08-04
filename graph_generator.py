import pandas as pd
import numpy as np
from matplotlib import rc
from matplotlib import pyplot as plt
import random
import json

plt.rcParams.update({'axes.labelsize' : 18, 'axes.titlesize': 18, 'font.family': 'serif'})

# TO-DO automate this
Pfile = open("dtmcprops.json")
Pfile = json.load(Pfile)
Rfile = open("1dtmcprops.json")
Rfile = json.load(Rfile)
Pminfile = open("1mdpprops.json")
Pminfile = json.load(Pminfile)
Pmaxfile = open("mdpprops.json")
Pmaxfile = json.load(Pmaxfile)
Rmaxfile = open("2mdpprops.json")
Rmaxfile = json.load(Rmaxfile)

def getProbs(file):
    keys = []
    for key in file:
        keys.append(key['v'])
    return keys

columns = ['Pmin', 'Pmax', 'P', 'Rmin', 'Rmax', 'R']
# d = pd.DataFrame(0, index=np.arange(len(data)), columns=feature_list)
df = pd.DataFrame(0, index=np.arange(len(Pfile)), columns=columns)
for i in df.index:
    p = getProbs(Pfile)[i]
    r = getProbs(Rfile)[i]
    pmin = getProbs(Pminfile)[i]
    pmax = getProbs(Pmaxfile)[i]
    rmin = 0
    rmax = getProbs(Rmaxfile)[i]
    df.loc[i,:] = [pmin, pmax, p, rmin, rmax, r]

def plot():
    # both graphs have the same layout (state ticks)
    state_labels = []
    states = []
    state_ticks = []
    for i in range(df.shape[0]):
        states.append(i)

    for i in range(df.shape[0]):
        if i*5 < df.shape[0] -1:
            state_labels.append(f"s{5*i + 1}")
            state_ticks.append(5*i + 1)
    
    # makes the lines go all the way to the axes
    plt.margins(0)

    # making two graphs to one png to print to the website
    fig, (axs1, axs2) = plt.subplots(1, 2, figsize = (100, 8), sharex = True, sharey = True)

    # first graph: plots P, Pmin, Pmax
    plt.xlim(0, df.shape[0])
    plt.xticks(state_ticks, state_labels)
    # plt.yticks([0.1,0.2], ['0.1','0.2'])
    plt.yticks([0.5, 1.0], ['0.5', '1.0'])
    # axs1.set_xlim(0,df.shape[0])

    axs1.fill_between(states, df['Pmin'], df['Pmax'], color = '#DBDBDB')
    axs1.plot(states, df['Pmin'], color = '#1a4314', marker = 'o', label = "Pmin", zorder=10, clip_on=False)
    axs1.plot(states, df['Pmax'], color = '#8d0000', marker = 'o', label = "Pmax", zorder=10, clip_on=False)
    axs1.plot(states, df['P'], color = '#ca06b8', marker = 'o', label = "P", zorder=10, clip_on=False)
    
    axs1.legend()

#     axs1.text(2.5, df['Pmax'][3] + 0.2, 'Pmax', color = '#8d0000', fontsize = 14)

    axs1.set_xlabel('States')
    
    axs1.set_ylabel('Probability')
    axs1.plot(1, 0, ">k", transform=axs1.get_yaxis_transform(), clip_on=False)
    axs1.set_title('titel')

    for spine in ['right', 'top']:
        axs1.spines[spine].set_visible(False)
        axs2.spines[spine].set_visible(False)

    # second graph: plots the rho data
  

    # axs2.set_xlim(0,df.shape[0])

    axs2.set_xlim(0, df.shape[0])
    ro1 = []
    roDiff = []
    for i in range(df.shape[0]):
        ro1 = (df['P'] - df['Pmin'])/(df['Pmax'] - df['Pmin'])
        roDiff = df['Pmax'] - df['Pmin']
        i += 1
    roDiffWidth = 0.25
    
    axs2.plot(states, ro1, color = '#ca06b8', marker = 'o', label = "rho1", zorder=10, clip_on=False)
    axs2.axhline(y = ro1.mean(), color = '#ca06b8', linestyle = '--', label = "rho1 Mean")
    
    axs2.legend()
    
    axs2.bar(states, roDiff, roDiffWidth, color = '#DBDBDB', edgecolor = '#BFBFBF')
    
#     axs2.text(2.5, .9, 'rho', color = '#ca06b8', fontsize = 14)

    axs2.set_xlabel('States')
    # plt.xticks(state_ticks, state_labels)
    # axs2.set_ylabel('Probability')
    axs2.plot(1, 0, ">k", transform=axs2.get_yaxis_transform(), clip_on=False)
    # plt.yticks([0.5, 1.0], ['0.5', '1.0'])
    # plt.yticks([0.1, 0.2], ['0.1','0.2'])
    axs2.set_title('titel')
        
    plt.savefig("graph.png")

# plot()


def firstPlot():
        # both graphs have the same layout (state ticks)
    state_labels = []
    states = []
    state_ticks = []
    for i in range(df.shape[0]):
        states.append(i)

    for i in range(df.shape[0]):
        if i*5 < df.shape[0] -1:
            state_labels.append(f"s{5*i + 1}")
            state_ticks.append(5*i + 1)
    
    # makes the lines go all the way to the axes
    plt.margins(0)

    # making two graphs to one png to print to the website
    fig, axs1 = plt.subplots(figsize = (20, 8))

    axs1.set_xlim(0,df.shape[0])
    # first graph: plots P, Pmin, Pmax
    # plt.xlim(0, df.shape[0])
    plt.xticks(state_ticks, state_labels)



    axs1.fill_between(states, df['Pmin'], df['Pmax'], color = '#DBDBDB')
    axs1.plot(states, df['Pmin'], color = '#1a4314', marker = 'o', label = "Pmin", zorder=10, clip_on=False)
    axs1.plot(states, df['Pmax'], color = '#8d0000', marker = 'o', label = "Pmax", zorder=10, clip_on=False)
    axs1.plot(states, df['P'], color = '#ca06b8', marker = 'o', label = "P", zorder=10, clip_on=False)
    
    axs1.legend()

#     axs1.text(2.5, df['Pmax'][3] + 0.2, 'Pmax', color = '#8d0000', fontsize = 14)

    axs1.set_xlabel('States')
    
    axs1.set_ylabel('Probability')
    axs1.plot(1, 0, ">k", transform=axs1.get_yaxis_transform(), clip_on=False)
    axs1.set_title('titel')
    plt.yticks([0.1,0.2], ['0.1','0.2'])
    # plt.yticks([0.5, 1.0], ['0.5', '1.0'])

    for spine in ['right', 'top']:
        axs1.spines[spine].set_visible(False)
        
    plt.savefig("graph.png")

def secondPlot():
    state_labels = []
    states = []
    state_ticks = []
    for i in range(df.shape[0]):
        states.append(i)

    for i in range(df.shape[0]):
        if i*5 < df.shape[0] -1:
            state_labels.append(f"s{5*i + 1}")
            state_ticks.append(5*i + 1)
    
    # makes the lines go all the way to the axes
    plt.margins(0)

    fig, axs2 = plt.subplots(figsize = (20, 8))
    
    axs2.set_xlim(0, df.shape[0])
    #  plt.xlim(0, df.shape[0])
    plt.xticks(state_ticks, state_labels)
    # plt.yticks([0.1,0.2], ['0.1','0.2'])
    plt.yticks([0.5, 1.0], ['0.5', '1.0'])


    ro1 = []
    roDiff = []
    for i in range(df.shape[0]):
        ro1 = (df['P'] - df['Pmin'])/(df['Pmax'] - df['Pmin'])
        # if ro1[i] > 1.0:
        #     ro1 = 0
        roDiff = df['Pmax'] - df['Pmin']
        i += 1
    roDiffWidth = 0.25
    
    ro1[46] = 0
    ro1[49] = 0
    axs2.plot(states, ro1, color = '#ca06b8', marker = 'o', label = "rho1", zorder=10, clip_on=False)
    axs2.axhline(y = ro1.mean(), color = '#ca06b8', linestyle = '--', label = "rho1 Mean")
    
    axs2.legend()
    
    axs2.bar(states, roDiff, roDiffWidth, color = '#DBDBDB', edgecolor = '#BFBFBF')
    
#     axs2.text(2.5, .9, 'rho', color = '#ca06b8', fontsize = 14)
    
    maxy = max(roDiff)

    axs2.set_xlabel('States')
    plt.xticks(state_ticks, state_labels)
    axs2.set_ylabel('Probability')
    axs2.plot(1, 0, ">k", transform=axs2.get_yaxis_transform(), clip_on=False)
    plt.yticks([0.5, 1.0], ['0.5', '1.0'])
    # plt.yticks([0.1, 0.2], ['0.1','0.2'])
    axs2.set_title('titel')

    for spine in ['right', 'top']:
        axs2.spines[spine].set_visible(False)
        
    plt.savefig("graph2.png")

firstPlot()
secondPlot()