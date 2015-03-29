from __future__ import print_function
from __future__ import division

import papersParse
from isiparse import parse_year, parse_month
from NetworkMakers import *
import StatisticsMethods as sm

import sys
from itertools import groupby
import networkx as nx

binByMonth = True

NETWORKS = [
        MakeCoAuth,
        MakeCoOrg,
        MakeCoCountry,
        ]

STATS = [
        sm.getBasicInfo,
        #sm.ExportGraphs,
        sm.getDensity,
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
        for stat in STATS:
            stat(networks)
        print("Done " + op.__name__)
