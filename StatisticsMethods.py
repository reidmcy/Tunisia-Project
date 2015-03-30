from __future__ import division
from __future__ import print_function

import numpy
import networkx as nx
import os
import pandas
import matplotlib.pyplot as plt
import matplotlib
import IPython

from scipy.stats import chisquare



def getBasicInfo(nets):
    for k in nets.keys():
        print(nx.info(nets[k]))
        print()



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
<<<<<<< HEAD
        l = list(l)
        if l:
            return sum(l)/len(l)
        else:
            return 0
=======
    return numpy.array(list(l)).mean()

def std(l): #omg why
    return numpy.array(list(l)).std()

def getDegree2d(nets):
    """
    make a 2d histogram with axes: date, degree
    """
    




# API:
# network -> scalar statistic

# tmap(size, networks -> series of statistic

#{k: stat(n) for for 


def chisq(series, p = 0.05):
    """
    ugly chisquared test on a single-dimensional dataset
    
    true if statistically significant
    """
    
    series = numpy.array(series) 
    L, cp = chisquare(series)
    # true if observed p-value (cp) is smaller than cutoff (p)
    return cp <= p
    
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
>>>>>>> d9bea74b82228b4ed3278d18dade4dc7fa78572a

def getAverageDegree(nets):
    #IPython.embed()
    print(str(list(nets.values())[0]).split('_')[0] + ' Average Degree')
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
