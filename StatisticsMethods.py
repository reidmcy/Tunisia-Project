import networkx as nx

def getBasicInfo(nets):
    for k in nets.keys():
        print nx.info(nets[k]) + '\n'
