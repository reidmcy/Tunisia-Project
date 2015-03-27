import networkx as nx

def MakeCoCountry(plst):
    retGrph = nx.Graph()
    for p in plst:
        try:
            for loc1 in p['C1']:
                c1 = loc1.split(', ')[-1][:-1]
                if c1[-3:] == 'USA':
                    c1 = 'USA'
                if not retGrph.has_node(c1):
                    retGrph.add_node(c1)
                for loc2 in p['C1'][p['C1'].index(loc1) + 1:]:
                    c2 = loc2.split(', ')[-1][:-1]
                    if c2[-3:] == 'USA':
                        c2 = 'USA'
                    if retGrph.has_edge(c1, c2):
                        retGrph[c1][c2]['weight'] += 1
                    else:
                        retGrph.add_edge(c1, c2, weight = 1)
        except KeyError as e:
            print "Key Error"
            print p.keys()
    return retGrph
