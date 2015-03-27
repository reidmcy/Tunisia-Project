from __future__ import print_function
from __future__ import division

from CoathMaker import *
from CoOrgMaker import *
from CoCountyMaker import *

import sys

from papersParse import *
from isiparse import *

from itertools import groupby
import networkx as nx

NETWORKS = [
        #MakeCoAuth,
        MakeCoCountry,
        MakeCoOrg,
        ]

STATS = [
        nx.density,
        nx.triangles,
        # add more stats methods here
        # (you might need to write lambdas to wrap the arguments appropriately)
        #TODO: per-node stats. do we average them? take distributions? Both?????
        ]

import pandas
import matplotlib.pyplot as plt

defaultFileType = '.isi'

if __name__ == "__main__":
    # load alllll the papers
    # as a 'table': a list of dictionaries
    papers = []
    #
    for fname in sys.argv[1:]:
        papers.extend(isiParser(fname))
    if len(sys.argv) == 1:
        for fname in getFiles(defaultFileType):
            papers.extend(isiParser(fname))
    # bin by month
    def reformat_crufty_date(paper):
        if 'PD' in paper and 'PY' in paper:
            year = paper['PY']
            year = year[0] #because stupidness

            month = paper['PD']
            month = month[0] #because stupidness
            return parse_year(year), parse_month(month)
        else:
            return None
    monthly_networks = groupby(papers, reformat_crufty_date)
    monthly_networks = {k: list(v) for k, v in monthly_networks} #expensively construct the full damn things in memory

    #print(monthly_networks)

    for op in NETWORKS:

        # rewrite the 'table' (for each month) as a nx object
        networks = {m: op(n) for m, n in monthly_networks.items()}

        # order by month (XXX probably better to presort before the loop)
        months = sorted(networks.keys()) #XXX and this sorted() is duplicating the next one
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

        del series['triangles'] #this won't fit into a DataFrame without more effort; in lieu of effort, delete it

        table = pandas.DataFrame(series, index=months)
        #import IPython; IPython.embed() #DEBUG

        #print(table) #DEBUG
        for col in table.columns:
            plt.figure()
            table[col].plot()
            plt.title(col)
        plt.show()
