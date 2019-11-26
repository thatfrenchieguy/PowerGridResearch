# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:58:57 2019

@author: BrianFrench
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from gurobipy import *
#define a powerset function
from itertools import chain, combinations
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#done as node, shift
###import the edge tracker
PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
Nodes = range(0,len(Grid.nodes))
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
          
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
            RoadGrid[i][j]['working']=True
        else:
            RoadGrid.add_edge(i,j,weight = 9999)
            RoadGrid[i][j]['working']=True
####Do a Routing Subproblem to confirm feasiblity of the postprocessed shift###
speed = 1/20
model = Model("mip1")
SP = np.zeros((len(Nodes), len(Nodes)))
for i in Nodes:
    for j in Nodes:
        SP[i][j] = nx.shortest_path_length(RoadGrid, source = i, target = j, weight='weight')
K = model.addVars(Nodes,Nodes,vtype=GRB.BINARY, name = "X")    
obj = model.setObjective(sum(SP[i][j]*K[i,j] for i in Nodes for j in Nodes),GRB.MINIMIZE)
for i in Nodes:
        model.addConstr(sum(K[i,j]for j in Nodes)-sum(K[j,i]for j in Nodes)==0)
        model.addConstr(K[i,i]==0)
PS = powerset(Nodes)
for s in PS:
 if len(s)<7:
  if len(s)>3:
    model.addConstr(sum(K[i,j] for i in s for j in s)<=len(s)-1)
###Node Constaints
model.addConstr(sum(K[13,j]for j in Nodes) >=1)

model.addConstr(sum(K[4,j]for j in Nodes) >=1)
###EdgeConstraints
model.addConstr(sum(K[11,j]for j in Nodes)+sum(K[15,j]for j in Nodes) >=0)   
model.addConstr(sum(K[13,j]for j in Nodes)+sum(K[14,j]for j in Nodes) >=0)   

model.optimize()
for i in Nodes:
    for j in Nodes:
        if K[i,j].X == 1:
            print([i,j])
print(model.objVal/20)






###PowerGrid PP
###Compute Load Shed###
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True
#Grid.node[4]['working']=False
#Grid.node[21]['working']=False
#Grid.node[20]['working']=False
#Grid.node[14]['working']=False
Grid.node[29]['working']=False
#Grid.node[9]['working']=False
#Grid[11][15][0]['working']=False
Grid[4][6][0]['working']=False
#Grid[21][23][0]['working']=False
#Grid[17][18][0]['working']=False
Grid[9][16][0]['working']=False
#Grid[14][17][0]['working']=False
#Grid[14][13][0]['working']=False
#Grid[11][14][0]['working']=False
Grid[1][3][0]['working']=False
#Grid[19][18][0]['working']=False
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])
#status tracker for edges since they've been seperated from the grid datastructure
EdgeStartingStatus = np.zeros(len(EdgeTracker))
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            for k in range(0,len(EdgeTracker)):
                if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
                    EdgeStartingStatus[k] = Grid[i][j][0]['working']
PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = list(range(0,len(PowerSub.edges)))
model = Model("mip1")
#define Variables
#Decision Variables
PG = model.addVars(Nodes,vtype=GRB.CONTINUOUS, name = "PG",lb = 0)
F_l = model.addVars(Edges, vtype=GRB.BINARY, name = "F_l")
F_n = model.addVars(Nodes, vtype= GRB.BINARY, name = "F_n")
Z = model.addVars(Nodes,Nodes, vtype = GRB.BINARY, lb = 0, ub=1, name = "Z") #abuse total unimodularity to speed up the solving time if needed
##State Variables
W_l = model.addVars(Edges, vtype = GRB.BINARY, name = "W_l")
W_n = model.addVars(Nodes, vtype = GRB.BINARY, name = "W_n")
Theta = model.addVars(Nodes, vtype = GRB.CONTINUOUS, name = "Theta")
PowerIJ = model.addVars(Edges, vtype = GRB.CONTINUOUS, name = "PowerIJ")
obj = model.setObjective(sum((1-W_n[i])*Grid.node[i]['load'] for i in Nodes),GRB.MINIMIZE)

M=10000
model.addConstr(Theta[0] == 0)
#for i in Nodes:
#    for j in Nodes:
#        for t in Time:
#         for k in range(0,len(EdgeTracker)):
#            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
#                    model.addConstr(PowerIJ[k,t] == Grid[i][j][0]['Sus']*(Theta[i,t]-Theta[j,t]))
#         model.addConstr(Theta[i,t]<=3.14)
#         model.addConstr(Theta[j,t]>=0)
#impose power balance constraints
for i in Nodes:
      originadj = []
      destadj = []
      for k in Edges:
          if EdgeTracker[k][1][0] == i:
              originadj.append(k)
          if EdgeTracker[k][1][1]==i:
              destadj.append(k)
      model.addConstr(PG[i]-sum(PowerIJ[j] for j in originadj)+sum(PowerIJ[k] for k in destadj) == Grid.node[i]['load']*W_n[i])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:
        model.addConstr(PG[i]<=Grid.node[i]['productionmax']*W_n[i])
        model.addConstr(PG[i]>=0)
#constrain line limits
for e in Edges:
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e])     
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]])     
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]])
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e])     
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]])    
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]])                
           

#define workingness
for i in Nodes:
    model.addConstr(W_n[i] <= Grid.node[i]['working'])    
for e in Edges:
        model.addConstr(W_l[e]<=int(EdgeStartingStatus[e]))
model.optimize()
print(model.objVal)        