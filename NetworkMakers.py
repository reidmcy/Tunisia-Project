
from __future__ import print_function
from __future__ import division

import networkx as nx

import os

__all__ = [
        "MakeCoAuth",
        "MakeCoOrg",
        "MakeCoCity",
        "MakeCoCountry",
        ]

def getInstitute(s):
    if s[0] == '[':
        s = s.split('] ')[1]
        c = len(s.split('] ')[0].split(','))
    else:
        c = 1
    clev = s.split(', ')
    if clev[-1] == 'Tunisia.':
        return (clev[0], c)
    else:
        return ''

def getCity(s):
    if s[0] == '[':
        s = s.split('] ')[1]
        c = len(s.split('] ')[0].split(','))
    else:
        c = 1
    clev = s.split(', ')
    if clev[-1] == 'Tunisia.':
        s = ''
        for w in clev[-2].split(' '):
            if not any(c.isdigit() for c in w):
                s += w + ' '
        return (s[:-1], c)
    else:
        return ''

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
    retGrph = nx.Graph(name = "CoCountry")
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
                            elif c1[0] != c2[0]:
                                retGrph.add_edge(c1[0], c2[0], weight = c1[1] + c2[1])
        except KeyError as e:
            #print "Key Error"
            #print p.keys()
            pass
    return retGrph

def MakeCoCity(plst):
    retGrph = nx.Graph(name = "CoCity")
    for p in plst:
        try:
            for i,loc1 in enumerate(p['C1']):
                c1 = getCity(loc1)
                if c1:
                    if not retGrph.has_node(c1[0]):
                        retGrph.add_node(c1[0])
                    for loc2 in p['C1'][i + 1:]:
                        c2 = getCity(loc2)
                        if c2:
                            if retGrph.has_edge(c1[0], c2[0]):
                                retGrph[c1[0]][c2[0]]['weight'] += c1[1] + c2[1]
                            elif c1[0] != c2[0]:
                                retGrph.add_edge(c1[0], c2[0], weight = c1[1] + c2[1])
        except KeyError as e:
            #print "Key Error"
            #print p.keys()
            pass
    return retGrph

def MakeCoOrg(plst):
    retGrph = nx.Graph(name = "CoOrg")
    for p in plst:
        try:
            for i,loc1 in enumerate(p['C1']):
                c1 = getInstitute(loc1)
                if c1:
                    if not retGrph.has_node(c1[0]):
                        retGrph.add_node(c1[0])
                    for loc2 in p['C1'][i + 1:]:
                        c2 = getInstitute(loc2)
                        if c2:
                            if retGrph.has_edge(c1[0], c2[0]):
                                retGrph[c1[0]][c2[0]]['weight'] += c1[1] + c2[1]
                            elif c1[0] != c2[0]:
                                retGrph.add_edge(c1[0], c2[0], weight = c1[1] + c2[1])
        except KeyError as e:
            #print "Key Error"
            #print p.keys()
            pass
    return retGrph

def MakeCoAuth(plst):
    retGrph = nx.Graph(name = "CoAuth")
    for p in plst:
        try:
            for i,auth1 in enumerate(p['AF']):
                if not retGrph.has_node(auth1):
                    retGrph.add_node(auth1)
                for auth2 in p['AF'][i + 1:]:
                    if not retGrph.has_node(auth2):
                        retGrph.add_node(auth2)
                    if retGrph.has_edge(auth1, auth2):
                        retGrph[auth1][auth2]['weight'] += 1
                    elif auth1 != auth2:
                        retGrph.add_edge(auth1, auth2, weight = 1)
        except KeyError as e:
            #print "Key Error"
            #print p.keys()
            pass
    return retGrph




if __name__ == '__main__':
    print("This is a utility module, not a program.")