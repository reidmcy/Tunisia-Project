#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import papersParse
from isiparse import parse_year, parse_month
import NetworkMakers
import StatisticsMethods as sm

import sys
from itertools import groupby
import networkx as nx
import matplotlib.pyplot as plt

from util import *

import argparse
import logging

# TODO:
# [ ] repair naming and titling of plots and output files
# [ ] pull ExportGraphs out

# ----------------------------------
# helpers

def vectorize(f):
    """
    turn a scalar operation into one across all the networks
    
    the returned operation (is meant to) work(s) on a dictionary {(year, month): networkx_graph}
    """
    def v(nets):
        return {k: f(n) for k, n in nets.items()}
    return v

def display(f):
    """
    turn a scalar operation into a printing one
    """
    def v(*args):
        r = f(*args)
        print(r)
        return r
    return v

def average(stat):
    return None

def stddev(stat):
    return None
    
def hist2d(stat):
    def ff(nets):
        
        dates = []
        stats = []
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
                dates.append(_date) #yes, this is intentionally making dupes
                stats.append(stat(nets[date], node))
        
        #IPython.embed()
        plt.figure()
        plt.hist2d(dates, degrees, norm=matplotlib.colors.LogNorm(), bins=15)
        plt.colorbar()
        
        #plt.title(str(list(nets.values())[0]).split('_')[0] + ' Degree Distributions over Time') #<-- TODO: repair
    return ff
    
# ----------------------------------


NETWORK_TYPES = {e: getattr(NetworkMakers, e) for e in NetworkMakers.__all__}
NETWORK_TYPES = { #DEBUG version
        #"Countries": MakeCoCountry,
        "Cities": NetworkMakers.MakeCoCity,
        #"Authors": MakeCoAuth,
        }


    
# (per-node -> {average, std dev, 2d histogram})
#  averge and std dev can be run through vectorize() but 2d histogram fundamentally cannot

# lists of analyses to run on the networks
# these are functions which take a dictionary {(year, month): networkx_graph}
# and *do something*
#
# within this, there are several obvious sub-categories:
# 

#<--- these two are almost perfectly correlated, which is a super strong suggestion that the degree distribution is exponential, which is the only(?) distribution with mean equal to standard deviation

GLOBAL_STATS = {
    'density': nx.density,
    'size': lambda G: len(G),
    }
    

    
PER_NODE_STATS = {
    'degree': lambda G, n: G.degree(n),
    '': None
    } 


# operations which take all bins of networks at once
# made by collecting the above stats and adding some more
ANALYSES = {
    'info': vectorize(display(nx.info)),
    #'export': sm.ExportGraphs,
    }
ANALYSES.update({k: vectorize(f) for k, f in GLOBAL_STATS.items()})
ANALYSES.update({"average_"+k: average(f) for k, f in PER_NODE_STATS.items()})
ANALYSES.update({"stddev_"+k: stddev(f) for k, f in PER_NODE_STATS.items()})
ANALYSES.update({"hist2d_"+k: hist2d(f) for k, f in PER_NODE_STATS.items()})


def node_remover(f, *nodes): #hmmmm. badly named?? or.. something? hmm
    """
    wrap network-creating function f so that it always eats nodes in nodes
    """
    def w(*args, **kwargs):
        G = f(*args, **kwargs)
        for node in nodes:
            if node in G:
                del G[node]
        return G
    return w

def parse_crufty_year(paper):
    """
    parse an ISI PY/PD pair into a tuple (year, month)
    gives *None* if unparseable (rather than raising an Exception)
     [this is ugly, but it's convenient since then we can just toss all the Nones]
    """
    year = None
    
    if 'PY' in paper:
        year = paper['PY']
        year = year[0] #because stupidness
        year = parse_year(year)
    
    return year


def parse_crufty_date(paper):
    """
    parse an ISI PY/PD pair into a tuple (year, month)
    gives *None* if unparseable (rather than raising an Exception)
     [this is ugly, but it's convenient since then we can just toss all the Nones]
    """
    month = None
    
    if 'PD' in paper:
        month = paper['PD']
        month = month[0] #because stupidness
        month = parse_month(month)
    
    return (parse_crufty_year(paper), month)

def filterNetworks(nets):
    """
        brutally remove bad data (to infinity and the sandwurms!)
    """
    retDict = {}
    for m in nets.keys():
        if m[0] != 2015 and m[0] != -1:
            retDict[m] = nets[m]
            if removeTunsia and retDict[m].has_node('Tunisia'):
                retDict[m].remove_node('Tunisia')
    return retDict

def bin_documents(documents, byMonth=True):
    """
    group documents by date
    
    documents: a sequence of ISI document objects (currently: as defined by papersParse)
    byMonth:   a flag which switches between grouping by month or by year.
    
    returns: a sequence of (date, [papers])
             beware: this is a generator, so you can exhaust it.
                     if you need it more than once, coerce the result to a list.
    """
    r = groupby(documents, parse_crufty_date if byMonth else parse_crufty_year)
    return {k: list(v) for k, v in r}.items()

def init(argv, ap=None):
    """
    common initialization code for all scripts in this project
    ap should be an argparse.ArgumentParser instance;
    (if not given, an empty one is created)
    common options are attached to the argument parser, and data is loaded
    """
    if ap is None:
        ap = argparse.ArgumentParser()
    
    if ap.description is None:
        ap.description = "Process .isi files for our project"
    
    
    ap.add_argument("-d", "--debug", action="store_true", help="Enable debug prints")
    ap.add_argument("-y", "--years", action="store_true", help="Bin by year; if false, will bin by month")
    ap.add_argument("--notunisia", action="store_true", help="Include Tunisia in co-country networks")
    ap.add_argument("papers", nargs="*", help="Files to load from. If not given, **the current directory is scanned for .isi files**")
    args = ap.parse_args(argv[1:])
    
    # special case: remove Tunisia from the Countries network
    # XXX can this be done cleaner? It's half-stateful...
    if args.notunisia and 'Countries' in NETWORK_TYPES:
        NETWORK_TYPES['Countries'] = node_remover(NETWORK_TYPES['Countries'], 'Tunisia')
    
    if args.debug:
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Enabled debugging output")
    
    # load papers
    if not args.papers: #scan the current directory
        args.papers = papersParse.getFiles()
    if not args.papers:
        #checks for any valid files
        print("No data files given.")
        ap.print_usage()
        sys.exit(-1)
    documents = flatten(papersParse.isiParser(fname) for fname in args.papers) #TODO: replace the inner seq with a generator so this doesn't lag so hard
    
    # DEBUG: fuzz the document set to shake out bugs
    # remove this for actual processing
    import random
    documents = list(documents)
    random.shuffle(documents)
    
    return args, documents

def valid_date(date, YEARS=(2006,2015)): #this is a python-style half open range: [startyear=2006, endyear=2015)
    if args.years:
        year = date
    else:
        year, month = date
        if month not in range(1,12+1): return False
    
    return year in range(*YEARS)

def main(argv):
    # enable nonblocking matplotlib
    # this makes *all plots appear at once* if -p is given
    plt.interactive(True)
    
    
    # read command line arguments and load data
    global args #XXX sketchy
    args = argparse.ArgumentParser(description="Compute statistics over time for our project")
    args.add_argument("-p", "--plots", action="store_true", help="Display plots; if false, plots will be saved to files")
    args, documents = init(argv, args)
    
    # group documents by month
    documents_over_time = bin_documents(documents, not args.years)
    
    
    # rewrite the paper bins as networks
    # we do this all at once for simplicity, but it might be possible to get this more efficient (however, remember that documents_over_time can only be iterated once
    networks = {(net_type, date): network_maker(paper_bin)
                                for date, paper_bin in documents_over_time
                                for net_type, network_maker in NETWORK_TYPES.items()
                                if valid_date(date) # clip to only the years we care about; as a useful side effect, remove invalid (e.g. unparseable) dates
                                }
    
    # for each (network type, date, statistic) compute and store the network single scalar value of that statistic measured on that network
    
    import IPython; IPython.embed()
    
    # make plots
    
    # block so the user can see plots
    # (we do this instead of just letting plt.show() block because this way all plots appear side-by-side)
    if args.plots:
        input("Press enter to quit, once you have observed the plots.")


if __name__ == "__main__":
    import sys
    main(sys.argv)