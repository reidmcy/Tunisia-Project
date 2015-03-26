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
        #coauth,
        MakeCoCountry,
        #coorg,
        ]

STATS = [
        nx.density,
        nx.triangles
        #TODO: per-node stats. do we average them? take distributions?
        ]

import pandas

if __name__ == "__main__":
    # load alllll the papers
    # as a 'table': a list of dictionaries
    papers = []
    #sys.argv[1:]
    for fname in getfiles():
        papers.extend(isiParse(fname))
        
    # bin by month
    monthly_networks = groupby(plst, lambda p: parse_month(p['PD'])
    
    
    for op in NETWORKS:
        print(op.__name__)
        
        # rewrite the 'table' (for each month) as a nx object
        networks = {m: op(n) for m, n in monthly_networks.items()}
        
        # order by month
        months = sorted(networks.keys()) #XXX this sorted() is duplicated
        networks = sorted(networks.items())
        
        # compute data series
        # one per desired statistic
        series = {stat.__name__: [stat(n) for m,n in networks] for stat in STATS}
        
        print(series)