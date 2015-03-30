from __future__ import division
from __future__ import print_function

import numpy
import networkx as nx
import os
import pandas
import matplotlib.pyplot as plt
import matplotlib
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
    return numpy.array(list(l)).mean()

def std(l): #omg why
    return numpy.array(list(l)).std()

def getDegree2d(nets):
    """
    make a 2d histogram with axes: date, degree
    """
    
    dates = []
    degrees = []
    for date in sorted(nets.keys()):
        if type(date) is tuple:
            # kludgily map (year,month) tuples to an absolute month index
            # pandas.plot() is smart enough to handle tuples
            # but pandas doesn't have hist2d, so we do this
            year, month = date
            _date = 12*(year - 2006) + month # < uugh 
        else:
            _date = date
        for node in nets[date]:
            degrees.append(nets[date].degree(node))
            
            dates.append(_date) #intentionally make dupes, so that hist2d
    
    #IPython.embed()
    plt.figure()
    plt.hist2d(dates, degrees, norm=matplotlib.colors.LogNorm(), bins=15)
    plt.colorbar()
    
    plt.title(str(list(nets.values())[0]).split('_')[0] + ' Degree Distributions over Time')
    plt.show()

def getSize(nets): #:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(:( :( :(
    #IPython.embed()
    stat = []
    time = []
    
    for k in nets.keys():
        stat.append(len(nets[k].degree().values()))
    d = pandas.DataFrame({'size': stat}, index = nets.keys())
    d = d.sort()
    #plt.figure() #duplicate??
    d.plot()
    plt.title(str(list(nets.values())[0]).split('_')[0] + ' Size')
    plt.show()

def getAverageDegree(nets):
    #IPython.embed()
    stat = []
    time = []
    for k in nets.keys():
        stat.append(mean(nets[k].degree().values()))
    d = pandas.DataFrame({'avgdegree': stat}, index = nets.keys())
    d = d.sort()
    #plt.figure() #duplicate??
    d.plot()
    plt.title(str(list(nets.values())[0]).split('_')[0] + ' Average Degree')
    plt.show()

def getStdDevDegree(nets): #:( :( :(
    #IPython.embed()
    stat = []
    time = []
    for k in nets.keys():
        stat.append(std(nets[k].degree().values()))
    d = pandas.DataFrame({'stddev_degree': stat}, index = nets.keys())
    d = d.sort()
    #plt.figure() #duplicate??
    d.plot()
    plt.title(str(list(nets.values())[0]).split('_')[0] + ' Degree Std Deviation')
    plt.show()
