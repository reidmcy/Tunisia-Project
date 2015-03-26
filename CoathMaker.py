import networkx as nx

def MakeCoAuth(plst):
    retGrph = nx.Graph()
    for p in plst:
        try:
            for i,auth1 in enumerate(p['AF']):
                if not retGrph.has_node(auth1):
                    retGrph.add_node(auth1)
                for auth2 in p['AF'][i + 1:]:
                    if not retGrph.has_node(auth2):
                        retGrph.add_node(auth2)
                    if retGrph.has_edge(auth1, auth2):
                        retGrph[auth1][auth2]['weight'] +=1
                    else:
                        retGrph.add_node(auth1, auth2, 1)
        except KeyError as e:
            print "Key Error"
            print p.keys()
    return retGrph
