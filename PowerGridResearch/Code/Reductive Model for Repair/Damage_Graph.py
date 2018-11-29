# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 10:05:30 2018

@author: Brian French
"""
import networkx as nx
import random

def DamageGraph(g):
    print(list(nx.neighbors(g,1)))
#    for node in list(g.nodes(data=True)):
    n=0
    while n<len(g):
        if g.node[n]['category'] == 'Generator':
            breakrand = random.randrange(1,101)
            if breakrand <=20:
                g.node[n]['working']=False
        if g.node[n]['category'] == 'Substation':
            breakrand = random.randrange(1,101)
            if breakrand <=40:
                g.node[n]['working']=False
        if g.node[n]['category'] == 'Transformer':
            breakrand = random.randrange(1,101)
            if breakrand <=40:
                g.node[n]['working']=False
        n=n+1
    return g

def TwoNodeBreak(g):
    nodelist = list(g.nodes())
    BrokenNode=random.sample(nodelist,2)
    for n in BrokenNode:
        g.node[n]['working']=False
    return g
