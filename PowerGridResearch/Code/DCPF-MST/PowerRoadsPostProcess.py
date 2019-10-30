# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:02:12 2019

@author: BrianFrench
"""


import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import csv
from gurobipy import *
#define a powerset function
from itertools import chain, combinations
def powerset(iterable):
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
Nodes = list(range(0,len(Grid.nodes)))
Time = list(range(0,PlanningHorizon))
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
        else:
            RoadGrid.add_edge(i,j,weight = 9999)
###commented out to have a fixed scenario based on the code below
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
#            print([i,j])
#            if np.random.uniform(0,10)<=2:
#                RoadGrid[i][j]['working']=False
#            else:
                RoadGrid[i][j]['working']=True
        else:
            RoadGrid[i][j]['working']=True
C = np.zeros((30,30))
for i in Nodes:
    for j in Nodes:
        if RoadGrid[i][j]['weight']<9000:
            C[i][j] = RoadGrid[i][j]['weight']
            
speed = 1/20
model = Model("mip1")
K = model.addVars(Nodes,Nodes,vtype=GRB.BINARY, name = "K")
S = model.addVars(Nodes,Nodes,vtype=GRB.CONTINUOUS, name = "S")
M=50000
obj = model.setObjective(sum(C[i][j]*K[i,j] for i in Nodes for j in Nodes),GRB.MINIMIZE)
for i in Nodes:
    for j in Nodes:
        model.addConstr(S[i,j] <= M*K[i,j]) 
        model.addConstr(S[i,j] >= RoadGrid[i][j]['weight']*speed*K[i,j])
model.addConstr(sum(S[i,j] for i in Nodes for j in Nodes)<=8)
for i in Nodes:
    model.addConstr(sum(K[i,j]for j in Nodes)-sum(K[j,i]for j in Nodes)==0)
model.addConstr(sum(K[13,j] for j in Nodes)==1)
PS = powerset(Nodes)
for s in PS:
 if len(s)<6:
  if len(s)>2:
    model.addConstr(sum(K[i,j] for i in s for j in s)<=len(s)-1)
    
###Nodes that need visited
model.addConstr(sum(K[7,j] for j in Nodes)==1)
###Lines that need visited
model.addConstr(sum(K[4,j] for j in Nodes)+sum(K[6,j] for j in Nodes)>=1)
#model.addConstr(sum(K[1,j] for j in Nodes)+sum(K[3,j] for j in Nodes)>=1)
setParam("NodefileStart", 5)
model.optimize()

for i in Nodes:
    for j in Nodes:
        if K[i,j].X >0:
            print([i,j,K[i,j].X])