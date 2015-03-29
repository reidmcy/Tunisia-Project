import networkx as nx
import os

outputDirectory = "OutputGraphs"

def sci2IsNotGood(fname):
    c = open(fname).readlines()
    f = open(fname, 'w')
    for l in c:
        if 'for="graph"' not in l and '<data key="d0">' not in l:
            f.write(l)

def getBasicInfo(nets):
    for k in nets.keys():
        print nx.info(nets[k]) + '\n'

def ExportGraphs(nets):
    if os.path.exists(outputDirectory):
        os.chdir(outputDirectory)
    else:
        os.mkdir(outputDirectory)
        os.chdir(outputDirectory)
    for v in nets.values():
        print "writing " + v.name
        nx.write_graphml(v, v.name + '.graphml')
        sci2IsNotGood(v.name + '.graphml') #modifie xml so sci2 can read it
    os.chdir('..')
