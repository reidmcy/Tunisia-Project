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
        nx.triangles,
        # add more stats methods here
        # (you might need to write lambdas to wrap the arguments appropriately)
        #TODO: per-node stats. do we average them? take distributions?
        ]

#import pandas

if __name__ == "__main__":
    # load alllll the papers
    # as a 'table': a list of dictionaries
    papers = []
    #
    for fname in sys.argv[1:]:
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
    monthly_networks = dict(monthly_networks)
    
    for op in NETWORKS:
        print()
        
        # rewrite the 'table' (for each month) as a nx object
        networks = {m: op(n) for m, n in monthly_networks.items()}
        import IPython; IPython.embed()
        
        # order by month
        months = sorted(networks.keys()) #XXX this sorted() is duplicated
        networks = sorted(networks.items())
        
        # compute data series
        # one per desired statistic
        series = {stat.__name__: [stat(n) for m,n in networks] for stat in STATS}
        
        # TODO: put into a pandas.DataFrame, then:
        # pandas.write_csv(series, op.__name__+".csv") -or-
        # pandas.plot()
        # in lieu of that:
        
        print(months) #<- keys
        print(series) #<- values