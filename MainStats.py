from __future__ import print_function
from __future__ import division

from NetworkMakers import *
import StatisticsMethods as sm


from isiparse import parse_year, parse_month

import sys
import time

import papersParse

from itertools import groupby
import networkx as nx

import pandas
import matplotlib.pyplot as plt

binByMonth = True

NETWORKS = [
        MakeCoAuth,
        MakeCoOrg,
        MakeCoCountry,
        ]

STATS = [
        #nx.density,
        #nx.triangles,
        #nx.info,
        sm.getBasicInfo,
        #sm.ExportGraphs
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
        return (parse_year(year), 0)
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

    for op in NETWORKS:

        # rewrite the 'table' (for each month) as a nx object
        networks = {m: op(n) for m, n in binNetworks.items()}
        # order by month (XXX probably better to presort before the loop)
        networks = {m: networks[m] for m in filter(lambda x: x[0] != 2015, networks.keys())}
        for m in networks.keys():
            if binByMonth:
                networks[m].name += '_' + str(m[0]) + '-' + str(m[1])
            else:
                networks[m].name += '_' + str(m[0])
            print(networks[m].name)
        #dates = sorted(networks.keys()) #XXX and this sorted() is duplicating the next one
        #networks = sorted(networks.items())

        # compute data series
        # one per desired statistic

        for stat in STATS:
            stat(networks)

        """
        series = {stat.__name__: [stat(n) for m,n in networks] for stat in STATS}

        #print(dates) #<- keys
        #print(series) #<- values

        # TODO: put into a pandas.DataFrame, then:
        # pandas.write_csv(series, op.__name__+".csv") -or-
        # pandas.plot()
        # in lieu of that:

        #del series['triangles'] #this won't fit into a DataFrame without more effort; in lieu of effort, delete it
        for v in series.values():
            print(v)


        table = pandas.DataFrame(series, index=dates)
        #print(table)
        #import IPython; IPython.embed() #DEBUG

        #print(table) #DEBUG
        for col in table.columns:
            plt.figure()
            table[col].plot()
            plt.title(op.__name__[4:] + ' ' + col)
        plt.show()
        """
        print("Done " + op.__name__)
