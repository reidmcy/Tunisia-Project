from __future__ import print_function
from __future__ import division

from CoathMaker import *
from CoOrgMaker import *
from CoCountyMaker import *

from isiparse import parse_year, parse_month

import sys
import time

import papersParse

from itertools import groupby
import networkx as nx

import pandas
import matplotlib.pyplot as plt

binByMonth = False

NETWORKS = [
        MakeCoAuth,
        MakeCoCountry,
        MakeCoOrg,
        ]

STATS = [
        nx.density,
        #nx.triangles,
        # add more stats methods here
        # (you might need to write lambdas to wrap the arguments appropriately)
        #TODO: per-node stats. do we average them? take distributions? Both?????
        ]

defaultFileType = '.isi'

def reformat_crufty_date(paper):
    if 'PD' in paper and 'PY' in paper and binByMonth:
        year = paper['PY']
        year = year[0] #because stupidness
        month = paper['PD']
        month = month[0] #because stupidness
        return parse_year(year), parse_month(month)
    elif 'PY' in paper:
        year = paper['PY'][0]
        return parse_year(year)
    else:
        return None

if __name__ == "__main__":
    # load alllll the papers
    # as a 'table': a list of dictionaries
    papers = []
    for fname in sys.argv[1:]:
        papers.extend(papersParse.isiParser(fname))
    if len(sys.argv) == 1:
        for fname in papersParse.getFiles(defaultFileType):
            papers.extend(papersParse.isiParser(fname))

    binNetworks = groupby(papers, reformat_crufty_date)
    binNetworks = {k: list(v) for k, v in binNetworks} #expensively construct the full damn things in memory

    #print(monthly_networks)

    for op in NETWORKS:

        # rewrite the 'table' (for each month) as a nx object
        networks = {m: op(n) for m, n in binNetworks.items()}
        # order by month (XXX probably better to presort before the loop)
        dates = sorted(networks.keys()) #XXX and this sorted() is duplicating the next one
        networks = sorted(networks.items())

        # compute data series
        # one per desired statistic
        series = {stat.__name__: [stat(n) for m,n in networks] for stat in STATS}

        #print(months) #<- keys
        #print(series) #<- values

        # TODO: put into a pandas.DataFrame, then:
        # pandas.write_csv(series, op.__name__+".csv") -or-
        # pandas.plot()
        # in lieu of that:

        #del series['triangles'] #this won't fit into a DataFrame without more effort; in lieu of effort, delete it

        table = pandas.DataFrame(series, index=dates)
        #import IPython; IPython.embed() #DEBUG

        #print(table) #DEBUG
        for col in table.columns:
            plt.figure()
            table[col].plot()
            plt.title(col)
        plt.show()
