#!/usr/bin/env python

import sys, os

from MainStats import init, load, NETWORK_TYPES #TODO: move these out of MainStats

import logging
import argparse

import networkx as nx

def sci2IsNotGood(fname):
    """
    modify xml so sci2 can read it
    Parsing xml without a parse is always a good idea
    """
    with open(fname) as c:
        with open(fname+".part", 'w') as f:
            for l in c:
                if 'for="graph"' not in l and '<data key="d0">' not in l:
                    f.write(l)
    os.rename(fname+".part",fname)


if __name__ == "__main__":
    # read command line arguments and load data
    import argparse
    global args #XXX sketchy
    args = argparse.ArgumentParser(description="Compute statistics over time for our project")
    args.add_argument("-o", dest="outputDirectory", help="Top level directory to place results in.", default="OutputGraphs")
    args = init(sys.argv, args)
    networks = load(*args.documents)
    
    if not os.path.exists(args.outputDirectory):
        os.mkdir(args.outputDirectory)
    
    for k, n in networks.items():
        fname = "_".join(map(str, k))
        fname +=  '.graphml'
        fname = os.path.join(args.outputDirectory, fname)
        logging.info("writing " + fname)
        nx.write_graphml(n, fname)
        sci2IsNotGood(fname)