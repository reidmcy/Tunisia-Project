#!/usr/bin/env python
"""
...
"""

# TODO:
# [ ] profile for speed; it's kinda slow on the larger networks...
# [ ] make significance testing work (and summarize nicely in pandas table)
#   -> this is tricky because our data are *not* independently sampled, which screws up most test
# [ ] make the hist2d thing work again
# [ ] make py2 compatible

from __future__ import print_function
from __future__ import division

import sys, os
import argparse
from itertools import groupby
import logging

import numpy
import matplotlib.pyplot as plt
import networkx as nx
import pandas

import papersParse
from isiparse import parse_year, parse_month
import NetworkMakers
import StatisticsMethods as sm

from util import *


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

def vectorize_per_node_stat(stat):
    def w(G):
        return numpy.array([stat(G,n) for n in G])
    return w

def average(stat):
    def w(G):
        return numpy.array(stat(G)).mean()
    return w
    
def stddev(stat):
    def w(G):
        return numpy.array(stat(G)).std()
    return w
    
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



NETWORK_TYPES = {
        "Countries": NetworkMakers.MakeCoCountry,
        "Cities": NetworkMakers.MakeCoCity,
        "Authors": NetworkMakers.MakeCoAuth,
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


def degree_centrality(G, *args, **kwargs):
    """
    monkey-patch degree_centrality() to properly handle single-node networks
    
    toads and hobgoblins! arg
    """
    if len(G)<2: return {n: 0 for n in G}
    return nx.degree_centrality._original(G, *args, **kwargs)
degree_centrality._original, nx.degree_centrality = nx.degree_centrality, degree_centrality;
del degree_centrality;

    
PER_NODE_STATS = { #these are computed suuuuuper inefficiently; maybe memoize them?
    'Degree Centrality': lambda G: list(nx.degree_centrality(G).values()),
    'Betweenness Centrality': lambda G: list(nx.betweenness_centrality(G).values()), #factorable?
    'Clustering Coefficient': lambda G: list(nx.clustering(G).values()),
    } 

STATS = {
    'Size': lambda G: len(G),
    'Density': nx.density,
    }
STATS.update({"Average "+k: average(f) for k, f in PER_NODE_STATS.items()})
STATS.update({"StdDev "+k: stddev(f) for k, f in PER_NODE_STATS.items()})
#STATS.update({"hist2d "+k: hist2d(f) for k, f in PER_NODE_STATS.items()}) #TODO

# operations which take all bins of networks at once
# made by collecting the above stats and adding some more
ANALYSES = {
    'info': vectorize(display(nx.info)),
    #'export': sm.ExportGraphs,
    }
#ANALYSES.update({k: vectorize(f) for k, f in GLOBAL_STATS.items()})


def node_remover(f, *nodes): #hmmmm. badly named?? or.. something? hmm
    """
    wrap network-creating function f so that it always eats nodes in nodes
    """
    def w(*args, **kwargs):
        G = f(*args, **kwargs)
        for node in nodes:
            if node in G:
                #del G[node]
                # whyyyyyyyyy
                G.remove_node(node)
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

def date(document, byMonth=True): #:( :(
    return (parse_crufty_date if byMonth else parse_crufty_year)(document)
    
    
def valid_date(date, YEARS=(2006,2015)): #this is a python-style half open range: [startyear=2006, endyear=2015)
    """
     clip to only the years we care about and remove invalid (e.g. unparseable) dates
    """
    
    try:
        year, month = date
        if month not in range(1,12+1): return False
    except (TypeError, ValueError): #:( :( @ "exceptions-as-returns"
        year = date
    
    return year in range(*YEARS)



def bin_documents(documents, byMonth=True):
    """
    group documents by date
    
    documents: a sequence of ISI document objects (currently: as defined by papersParse)
    byMonth:   a flag which switches between grouping by month or by year.
    
    returns: a dictionary {date: [documents]}
    
    precondition: all documents have valid dates (as according to valid_date)
    """
    date_term = lambda d: date(d, byMonth) #key function
    
    r = sorted(documents, key = date_term) #we need to sort first because groupby is *not* the same as a SQL groupby; rather it's like unix `uniq`
    r = groupby(r, key = date_term)
    r = dict((k, list(v)) for k,v in r) #since groupbys is a sneaky jerk---iterating over the outer elements implicitly iterates over the inner ones, losing them forever---express it to a dict.
    return r


def load(*documents):
    """
    load documents from the given list of filenames
    """
    global args
    
    documents = flatten(papersParse.isiParser(fname) for fname in documents) #TODO: replace the inner seq with a generator so this doesn't lag so hard
    
    if args.debug:
        # DEBUG
        logging.debug("fuzzing document set to shake out bugs")
        import random
        documents = list(documents) #observation: even on 30000 records, this shuffle barely adds anything to the runtime.
        N = len(documents)
        random.shuffle(documents)
    
    # filter out badly dated documents
    # This tends to cull our dataset significantly, but, at least on the datasets we've checked,
    # uniformly, so all normalized statistics should be un(statistically-speaking)affected.
    documents = (d for d in documents if valid_date(date(d, not args.years)))
    if args.debug:
        documents = list(documents)
        logging.debug("%02.02f%% of our documents had invalid dates, and were rejected.", 100*(1 - len(documents)/N))
    
    # group documents by date
    if args.debug:
        #DEBUG: ensure we get the same number of documents back
        documents = list(documents) #express fully that we may interrogate yet still use it
        N = len(documents)
    logging.debug("grouping documents by date")
    documents_over_time = bin_documents(documents, not args.years)
    if args.debug:
        assert sum(len(docs) for date,docs in documents_over_time.items()) == N, "Binned documents should add up to the original count (%d); instead got %d" % (N, sum(len(docs) for date,docs in documents_over_time))
    
    # rewrite the paper bins as networks
    # we do this all at once for simplicity, but it might be possible to get this more efficient (however, remember that documents_over_time can only be iterated once
    logging.debug("transforming groups into networks")
    networks = {(net_type, date): network_maker(bin)
                                for date, bin in documents_over_time.items()
                                for net_type, network_maker in NETWORK_TYPES.items()
                                }
    
    return networks

def init(argv, ap=None):
    """
    common initialization code for all scripts in this project
    ap should be an argparse.ArgumentParser instance;
    (if not given, an empty one is created)
    common options are attached to the argument parser, and data is loaded
    """
    global args #XXX sketchy
    
    if ap is None:
        ap = argparse.ArgumentParser()
    
    if ap.description is None:
        ap.description = "Process .isi files for our project"
    
    ap.add_argument("-d", "--debug", action="store_true", help="Enable debug prints")
    ap.add_argument("-y", "--years", action="store_true", help="Bin by year; if false, will bin by month")
    ap.add_argument("--notunisia", action="store_true", help="Remove Tunisia from co-country networks")
    ap.add_argument("documents", nargs="*", help="Files to load from. If not given, **the current directory is scanned for .{isi,ciw} files**")
    args = ap.parse_args(argv[1:])
    
    
    # special case: remove Tunisia from the Countries network
    # XXX can this be done cleaner? It's half-stateful...
    if args.notunisia and 'Countries' in NETWORK_TYPES:
        NETWORK_TYPES['Countries'] = node_remover(NETWORK_TYPES['Countries'], 'Tunisia')
    
    if args.debug:
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Enabled debugging output")
        logging.debug("Received these arguments: %s", args)
    
    if not args.documents:
        #fall back on scanning the current directory
        args.documents = [f for f in os.listdir(".") if (f.endswith(".isi") or f.endswith(".ciw"))]
    if not args.documents:
        print("No data files found.")
        ap.print_usage()
        sys.exit(-1)
    
    # load papers
    return args, load(*args.documents)


if __name__ == "__main__":
    
    # read command line arguments and load data
    global args #XXX sketchy
    ap = argparse.ArgumentParser(description="Compute statistics over time for our project.")
    ap.add_argument("-p", "--plots", action="store_true", help="Display plots; if false, plots will be saved to files")
    ap.add_argument("-N", metavar="NET", action="append", help="Enable network type %(metavar)s; default is all options.", choices = sorted(NETWORK_TYPES))
    ap.add_argument("-S", metavar="STAT", action="append", help="Enable statistic %(metavar)s; default is all options.", choices = sorted(STATS))
    args, networks = init(sys.argv, ap)
    
    # XXX dirtyyyyy: filter the things, throwing away the functions entirely
    if args.N:
        NETWORK_TYPES = {n: NETWORK_TYPES[n] for n in args.N}
    if args.S:
        STATS = {s: STATS[s] for s in args.S}
    
    logging.debug("Enabled network types: %s", ", ".join(sorted(NETWORK_TYPES))) #TODO: factor
    logging.debug("Enabled statistics: %s", ", ".join(sorted(STATS)))
    
    if args.plots:
        # enable nonblocking matplotlib (and manually hang at the end of the script instead)
        # this makes *all plots appear at once* if -p is given
        plt.interactive(True)
    
    # for each (network type, date, statistic) compute and store the network single scalar value of that statistic measured on that network
    logging.debug("computing statistics")
    statistics = {(net_type, date, stat_name): stat(net)
                                            for stat_name, stat in STATS.items()
                                            for (net_type, date), net in networks.items()
                                            }
    
    # reflow that dict into a DataFrame
    # tip adapted from http://stackoverflow.com/questions/19961490/construct-pandas-dataframe-from-list-of-tuples
    logging.debug("reflowing statistics to a DataFrame")
    statistics = pandas.DataFrame(list(k+(v,) for k,v in statistics.items()), columns=["network","date","statistic","value"])
    # and of course we have to bang it with pots and pans to make it behave
    statistics["network"] = statistics["network"].astype("category")
    statistics["statistic"] = statistics["statistic"].astype("category")
    statistics = statistics.sort(["network","statistic","date"])
    statistics = statistics.set_index(["network","date","statistic"])

    # for each *statistic* display its progress with each type of network as a different line
    statistics = statistics.unstack("network")
    statistics.columns = [net_type for (value, net_type) in statistics.columns] # kludge over a weirdness: unstack() results in naming (i.e. indexing) the column as (value, Network); this causes ugliness when plotting, so stab it good
    for stat_name in statistics.index.levels[-1]:
        subset = statistics.loc[(slice(None),stat_name),:] #the slice(None) is a wart of pandas: loc can both index only down rows (the "index") or across rows and columns, and which it does is slightly ambiguous; the docs warn about this: http://pandas.pydata.org/pandas-docs/stable/advanced.html "You should specify all axes in the .loc specifier, meaning the indexer for the index and for the columns. Their are some ambiguous cases where the passed indexer could be mis-interpreted as indexing both axes, rather than into say the MuliIndex for the rows." LIKE A JERK
        
        # similar to the above, this hackily silences the static labels
        subset, subset.columns = subset.unstack("statistic"), subset.columns
        
        logging.debug("%s results", stat_name) #omg why is this not the same API as print()?
        logging.debug(subset)
        
        subset.plot(title=stat_name)
        
        if not args.plots:
            plt.savefig("%s.svg" % stat_name)
    
    
    # block so the user can see plots
    # (we do this instead of just letting plt.show() block because this way all plots appear side-by-side)
    if args.plots:
        input("Press enter to quit, once you have observed the plots. ")

