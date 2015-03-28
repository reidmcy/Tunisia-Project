import networkx as nx

def getCountry(s):
    if s[0] == '[':
        s = s.split('] ')[1]
        c = len(s.split('] ')[0].split(','))
    else:
        c = 1
    clev = s.split(', ')
    if clev[-1][-4:] == 'USA.':
        return ('USA', c)
    else:
        return (clev[-1][:-1], c)

def MakeCoCountry(plst):
    retGrph = nx.Graph()
    for p in plst:
        try:
            for i,loc1 in enumerate(p['C1']):
                c1 = getCountry(loc1)
                if c1:
                    if not retGrph.has_node(c1[0]):
                        retGrph.add_node(c1[0])
                    for loc2 in p['C1'][i + 1:]:
                        c2 = getCountry(loc2)
                        if c2:
                            if retGrph.has_edge(c1[0], c2[0]):
                                retGrph[c1[0]][c2[0]]['weight'] += c1[1] + c2[1]
                            else:
                                retGrph.add_edge(c1[0], c2[0], weight = c1[1] + c2[1])
        except KeyError as e:
            print "Key Error"
            print p.keys()
    return retGrph
