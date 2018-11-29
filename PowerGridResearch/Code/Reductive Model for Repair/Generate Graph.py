# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 10:09:01 2018

@author: Brian French
"""
import networkx as nx
import matplotlib.pyplot as plt
import random
def BasicGrid(subs, trans):
    NumSubstations=subs
    NumTransformers=trans
    #let generator be node zero
    NodeList=['Generator']
    EdgeList=[]
    i=0
    while i<=NumSubstations:
       StrSubstation = "Substation_"+str(i)
       NodeList.append(StrSubstation)
       EdgeList.append([StrSubstation,'Generator'])
       i=i+1
    i=0
    while i<=NumTransformers:
        StrTransformer = "Transformer_"+str(i)
        NodeList.append(StrTransformer)
        rand = random.randrange(0,NumSubstations-1)
        RandSS = "Substation_"+str(rand)
        EdgeList.append([StrTransformer, RandSS])
        i=i+1
    Grid = nx.Graph()
    print(EdgeList)
    Grid.add_nodes_from(NodeList)
    Grid.add_edges_from(EdgeList)
    nx.draw(Grid)
    plt.show()
        
        