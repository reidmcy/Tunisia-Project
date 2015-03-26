import networkx as nx

def getInstitute(s):
    if s[0] == '[':
        s = s.split('] ')[1]
    clev = s.split(', ')
    if clev[-1] == 'Tunisia.':
        return clev[0]
    else:
        return ''

def MakeCoOrg(plst):
    retGrph = nx.Graph()
    for p in plst:
        try:
            for loc1 in p['C1']:
                c1 = getInstitute(loc1)
                if c1:
                    if not retGrph.has_node(c1):
                        retGrph.add_node(c1)
                    for loc2 in p['C1'][p['C1'].index(loc1) + 1:]:
                        c2 = getInstitute(loc2)
                        if c2:
                            if retGrph.has_edge(c1, c2):
                                retGrph[c1][c2]['weight'] += 1
                            else:
                                print str(c1) + ' - ' + str(c2)
                                retGrph.add_edge(c1, c2, weight = 1)
        except KeyError as e:
            print "Key Error"
            print p.keys()
    return retGr
