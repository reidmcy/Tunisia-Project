from __future__ import division
from __future__ import print_function

import networkx as nx
import os
import pandas
import matplotlib.pyplot as plt
import IPython

outputDirectory = "OutputGraphs"

def sci2IsNotGood(fname):
    """
    Parsing xml without a parse is always a good idea
    """
    c = open(fname).readlines()
    f = open(fname, 'w')
    for l in c:
        if 'for="graph"' not in l and '<data key="d0">' not in l:
            f.write(l)

def getBasicInfo(nets):
    for k in nets.keys():
        print(nx.info(nets[k]))
        print()

def ExportGraphs(nets):
    if os.path.exists(outputDirectory):
        os.chdir(outputDirectory)
    else:
        os.mkdir(outputDirectory)
        os.chdir(outputDirectory)
    for v in nets.values():
        print("writing " + v.name)
        nx.write_graphml(v, v.name + '.graphml')
        sci2IsNotGood(v.name + '.graphml') #modifie xml so sci2 can read it
    os.chdir('..')

def getDensity(nets):
    dates = sorted(nets.keys()) #XXX and this sorted() is duplicating the next one
    networks = sorted(nets.items())
    series = {stat.__name__: [stat(n) for m,n in networks] for stat in [nx.density]}
    table = pandas.DataFrame(series, index=dates)
    for col in table.columns:
        plt.figure()
        table[col].plot()
        plt.title(str(networks[0][1]).split('_')[0] + ' ' + col)
    plt.show()

def mean(l):
        l = list(l)
        return sum(l)/len(l)

def getAverageDegree(nets):
    #IPython.embed()
    stat = []
    time = []
    for k in nets.keys():
        stat.append(mean(nets[k].degree().values()))
    d = pandas.DataFrame({'avgdegree': stat}, index = nets.keys())
    d = d.sort()
    plt.figure()
    d.plot()
    plt.title(str(list(nets.values())[0]).split('_')[0] + ' Average Degree')
    plt.show()
