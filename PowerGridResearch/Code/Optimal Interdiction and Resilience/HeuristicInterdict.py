# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

### solve current DCPowerFlow
### choose lines and nodes with highest flow ratio and highest demand nodes
### pick number to interdict (representing high priority fortification in resilience models) and pick the top N+K (for 3 lines, top 6, 2 nodes, top 4)
### test every combination in loop and choose best to represent the fortification choices

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import csv
from operator import itemgetter
from gurobipy import *
#define a powerset function
from itertools import chain, combinations
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#initialize graph from file
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)

PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = list(range(0,len(PowerSub.edges)))
Nodes = list(range(0,30))
model = Model("mip1")
#define Variables
#Decision Variables
PG = model.addVars(Nodes,vtype=GRB.CONTINUOUS, name = "PG",lb = 0)
##State Variables
W_l = model.addVars(Edges, vtype = GRB.BINARY, name = "W_l")
W_n = model.addVars(Nodes, vtype = GRB.BINARY, lb = 0, ub=1, name = "W_n")
Theta = model.addVars(Nodes, vtype = GRB.CONTINUOUS, name = "Theta")
PowerIJ = model.addVars(Edges, vtype = GRB.CONTINUOUS, name = "PowerIJ")
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True

setParam("MIPGap", .005)
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
obj = model.setObjective(sum((1-W_n[i])*Grid.node[i]['load'] for i in Nodes),GRB.MINIMIZE)


#impose phase angle constraints

M=10000

model.addConstr(Theta[0] == 0)
for i in Nodes:
    for j in Nodes:
         for k in range(0,len(EdgeTracker)):
            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
#                    print([i,j])
                    model.addConstr(PowerIJ[k] >= 250*Grid[i][j][0]['Sus']*(Theta[j]-Theta[i])-5*M*W_l[k])
                    model.addConstr(PowerIJ[k] <= M*W_l[k])
                    model.addConstr(PowerIJ[k] <= 250*Grid[i][j][0]['Sus']*(Theta[j]-Theta[i]))
#                    model.addConstr(PowerIJ[k,t] <= 1.05*500*Grid[i][j][0]['Sus']*(Theta[j,t]-Theta[i,t])*W_l[k,t])
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
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e]*1.2)     
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]]*1.2)     
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]]*1.2)
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e]*1.2)     
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]]*1.2)     
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]]*1.2)                
           

#define workingness
for i in Nodes:
    model.addConstr(W_n[i] <= Grid.node[i]['working'])
for e in Edges:
        model.addConstr(W_l[e]<=int(EdgeStartingStatus[e]))
model.optimize()

FlowRatio=[]
for e in Edges:
    i = EdgeTracker[e][1][0]
    j = EdgeTracker[e][1][1]
    flow = PowerIJ[e].X
    maxflow = Grid[i][j][0]['capacity']
    ratio = flow/(maxflow*1.2)
    FlowRatio.append([e,i,j,ratio])
SortedFlowRatio = sorted(FlowRatio, key = itemgetter(3))
SortedFlowRatio.reverse() # put it in ascending order to make life easier
listofnodes = list(Grid.nodes)
ListOfNodesWithDemand = []
for n in listofnodes:
    node = n
    demand = Grid.node[n]['load']
    ListOfNodesWithDemand.append([node,demand])
SortedNodes = sorted(ListOfNodesWithDemand, key = itemgetter(1))
SortedNodes.reverse()



### time to interdict
NumberNodesInterdict = 2
NumberEdgesInterdict = 4

TrimmedNodes = SortedNodes[:3*NumberNodesInterdict]
TrimmedEdges = SortedFlowRatio[:3*NumberEdgesInterdict]

ListOfNodeInterdict = [list(i) for i in combinations(TrimmedNodes, NumberNodesInterdict)]
ListOfEdgeInterdict = [list(j) for j in combinations(TrimmedEdges, NumberEdgesInterdict)]
LargestDamage = -1
WorstNodes = []
WorstEdges = []
for nodeset in ListOfNodeInterdict:
    for edgeset in ListOfEdgeInterdict:
        for n in Grid.nodes:
            Grid.node[n]['working']=True
        for e in Grid.edges:
            if PowerSub.has_edge(e[0],e[1]):
                Grid[e[0]][e[1]][e[2]]['working'] = True
        for breaknode in nodeset:
            Grid.node[breaknode[0]]['working'] = False
        for breakedge in edgeset:
            EdgeEnd1 = EdgeTracker[breakedge[0]][1][0]
            EdgeEnd2 = EdgeTracker[breakedge[0]][1][1]
            Grid[EdgeEnd1][EdgeEnd2][0]['working'] = False
       
        
        
        
        
        model = Model("mip1")
        #define Variables
        #Decision Variables
        PG = model.addVars(Nodes,vtype=GRB.CONTINUOUS, name = "PG",lb = 0)
        ##State Variables
        W_l = model.addVars(Edges, vtype = GRB.BINARY, name = "W_l")
        W_n = model.addVars(Nodes, vtype = GRB.BINARY, lb = 0, ub=1, name = "W_n")
        Theta = model.addVars(Nodes, vtype = GRB.CONTINUOUS, name = "Theta")
        PowerIJ = model.addVars(Edges, vtype = GRB.CONTINUOUS, name = "PowerIJ")
        obj = model.setObjective(sum((1-W_n[i])*Grid.node[i]['load'] for i in Nodes),GRB.MINIMIZE)
        EdgeStartingStatus = np.zeros(len(EdgeTracker))
        for i in Nodes:
            for j in Nodes:
                if Grid.has_edge(i,j,0):
                    for k in range(0,len(EdgeTracker)):
                        if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
                            EdgeStartingStatus[k] = Grid[i][j][0]['working']
        
                #impose phase angle constraints
        
        M=10000
        
        model.addConstr(Theta[0] == 0)
        for i in Nodes:
            for j in Nodes:
                 for k in range(0,len(EdgeTracker)):
                    if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
        #                    print([i,j])
                            model.addConstr(PowerIJ[k] >= 250*Grid[i][j][0]['Sus']*(Theta[j]-Theta[i])-5*M*W_l[k])
                            model.addConstr(PowerIJ[k] <= M*W_l[k])
                            model.addConstr(PowerIJ[k] <= 250*Grid[i][j][0]['Sus']*(Theta[j]-Theta[i]))
        #                    model.addConstr(PowerIJ[k,t] <= 1.05*500*Grid[i][j][0]['Sus']*(Theta[j,t]-Theta[i,t])*W_l[k,t])
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
                        model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e]*1.2)     
                        model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]]*1.2)     
                        model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]]*1.2)
                        model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e]*1.2)     
                        model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]]*1.2)     
                        model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]]*1.2)                
                   
        
        #define workingness
        for i in Nodes:
            model.addConstr(W_n[i] <= Grid.node[i]['working'])
        for e in Edges:
                model.addConstr(W_l[e]<=int(EdgeStartingStatus[e]))
        model.optimize()
        if model.objVal > LargestDamage:
            LargestDamage = model.objVal
            WorstNodes = nodeset
            WorstEdges = edgeset
        