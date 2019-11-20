# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 10:32:28 2019

@author: BrianFrench
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
#from gurobipy import *
from scipy import stats
#define a powerset function
from itertools import chain, combinations
def powerset(iterable):
    "list(powerset([1,2,3])) --> [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#initialize graph from file
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 6 #this is measured in shifts
ShiftLength = 8 #in Hours
#Define sets to be used in optimiation
PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = list(range(0,len(PowerSub.edges)))
Nodes = list(range(0,30))
sumlen = 71

###define a strikepath###
##maximum Xcoord = 20
##maximum ycoord = 24
StrikeStart = (20,30)
p1 = np.asarray(StrikeStart)
StrikeEnd = (0,30)
p2 = np.asarray(StrikeEnd)
MaxWind = 140 #in M/s
BaseWind = 3 #f constant in Scherb et al 2015
HurricaneRadius = 40 #in Km from the same paper as Rmax
for n in PowerSub.nodes:
    print(n)
    nodeX = PowerSub.node[n]['xcoord']
    nodeY = PowerSub.node[n]['ycoord']
    p3 = np.array([nodeX,nodeY])
    #calculuate distance from the strike path
    d=abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
    LocalWind = (2*d*HurricaneRadius*(MaxWind-BaseWind))/(math.pow(d,2)+math.pow(HurricaneRadius,2))
    Grid.node[n]['WindSpeed'] = LocalWind
    ## calculate failure probabilities
    mu =4.3
    sigma = .4
    dist=stats.norm(mu, sigma)
    ProbabilityDamage = dist.cdf(math.log(Grid.node[n]['WindSpeed']))
    Grid.node[n]['FailureChance']=ProbabilityDamage
for e in Grid.edges:
    EdgeWind = max(Grid.node[e[0]]['WindSpeed'],Grid.node[e[1]]['WindSpeed'])
    mu =3.8
    sigma = .22
    dist=stats.norm(mu, sigma)
    ProbabilityDamage = dist.cdf(math.log(EdgeWind))
    Grid[e[0]][e[1]][e[2]]['FailureChance'] = ProbabilityDamage
    
for n in Grid.nodes:
    p = np.random.uniform()
    if p >= Grid.node[n]['FailureChance']:
        Grid.node[n]['Working']=True
    else:
        Grid.node[n]['Working'] = False
        print([n,'is broken'])
for e in Grid.edges:
    if Grid[e[0]][e[1]][e[2]]['Type'] == 'Power':
         p = np.random.uniform()
         if p >= Grid[e[0]][e[1]][e[2]]['FailureChance']:
             Grid[e[0]][e[1]][e[2]]['Working']=True
         else:
             Grid[e[0]][e[1]][e[2]]['Working']=False
             print([e[0],e[1],'is broken'])