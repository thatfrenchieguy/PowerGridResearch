# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 15:14:39 2019

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
#sumlen = len(Nodes)+len(Edges)
NodesWithDummy = list(range(0,sumlen))
Time = list(range(0,PlanningHorizon))
model = Model("mip1")
#define Variables
#Decision Variables
PG = model.addVars(Nodes,Time,vtype=GRB.CONTINUOUS, name = "PG",lb = 0)
F_l = model.addVars(Edges,Time, vtype=GRB.BINARY, name = "F_l")
F_n = model.addVars(Nodes,Time, vtype= GRB.BINARY, name = "F_n")
Z = model.addVars(NodesWithDummy,NodesWithDummy,Time, vtype = GRB.BINARY, lb = 0, ub=1, name = "Z") #abuse total unimodularity to speed up the solving time if needed
##State Variables
W_l = model.addVars(Edges,Time, vtype = GRB.BINARY, name = "W_l")
W_n = model.addVars(Nodes, Time, vtype = GRB.BINARY, name = "W_n")
Theta = model.addVars(Nodes,Time, vtype = GRB.CONTINUOUS, name = "Theta")
PowerIJ = model.addVars(Edges,Time, vtype = GRB.CONTINUOUS, name = "PowerIJ")
MST = model.addVars(Time, vtype = GRB.CONTINUOUS, lb=0, name = "MST")
#default everything to working
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True
##artblock
x  = nx.get_node_attributes(Grid,('xcoord'))
y = nx.get_node_attributes(Grid,'ycoord')
pos=[]
power = []
road = []
for i in x:
    pos.append((x[i],y[i]))
for e in Grid.edges:
    if e[2]==0:
        power.append(e)
    if e[2]==1:
        road.append(e)
        
nx.draw_networkx_nodes(Grid, pos, label=True)
nx.draw_networkx_labels(Grid, pos)
nx.draw_networkx_edges(Grid, pos, edgelist = power, edge_color = "g", width = 2, alpha =.7)
nx.draw_networkx_edges(Grid, pos, edgelist = road, edge_color = 'r', width = 2, alpha = .7)
#
plt.axis('off')
plt.show()
#######            
###SCENARIO OF BROKEN THINGS###
Grid.node[6]['working']=False
Grid.node[27]['working']=False
Grid.node[23]['working']=False
Grid.node[18]['working']=False
Grid.node[15]['working']=False
Grid[1][4][0]['working']=False
Grid[4][6][0]['working']=False
Grid[7][27][0]['working']=False
Grid[24][25][0]['working']=False
Grid[11][15][0]['working']=False
Grid[1][3][0]['working']=False
Grid[19][18][0]['working']=False
###END SCENARIO###            

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
###Build broken elements into a list for STE constraints####
STE = []
for i in range(len(Grid.nodes())):
    if Grid.node[i]['working']==False:
        STE.append(i)
for j in range(len(EdgeStartingStatus)):
    if EdgeStartingStatus[j]==0:
        STE.append(30+j)
###End STE building###


obj = model.setObjective(sum((1-W_n[i,t])*Grid.node[i]['load'] for i in Nodes for t in Time),GRB.MINIMIZE)


#impose phase angle constraints

M=1000
for i in Nodes:
    for j in Nodes:
        for t in Time:
         for k in range(0,len(EdgeTracker)):
            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
                    model.addConstr(PowerIJ[k,t] == Grid[i][j][0]['Sus']*(Theta[i,t]-Theta[j,t]))
        model.addConstr(Theta[i,t]<=3.14)
        model.addConstr(Theta[j,t]>=0)
#impose power balance constraints
for i in Nodes:
    for t in Time:
      originadj = []
      destadj = []
      for k in Edges:
          if EdgeTracker[k][1][0] == i:
              originadj.append(k)
          if EdgeTracker[k][1][1]==i:
              destadj.append(k)
      model.addConstr(PG[i,t]-sum(PowerIJ[j,t] for j in originadj)+sum(PowerIJ[k,t] for k in destadj) == Grid.node[i]['load']*W_n[i,t])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:
    for t in Time:
        model.addConstr(PG[i,t]<=Grid.node[i]['productionmax']*W_n[i,t])
        model.addConstr(PG[i,t]>=0)
#constrain line limits
for e in Edges:
        for t in Time:
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e,t])     
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0],t])     
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1],t])
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e,t])     
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0],t])     
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1],t])                
           

#define workingness
for i in Nodes:
    model.addConstr(W_n[i,0] <= Grid.node[i]['working'])
    for t in range(1,len(Time)):
        model.addConstr(W_n[i,t]<=sum(F_n[i,g] for g in range(0,t))+Grid.node[i]['working'])
for e in Edges:
    for t in Time:
        model.addConstr(W_l[e,t]<=sum(F_l[e,g] for g in range(0,t))+EdgeStartingStatus[e])
        
#schedule restriction so that nothing gets double fixed
for i in Nodes:
    model.addConstr(sum(F_n[i,t]for t in Time)<=1)   
for e in Edges:
    model.addConstr(sum(F_l[e,t]for t in Time)<=1)         
#build shortest path matrix
SP = np.zeros((len(NodesWithDummy), len(NodesWithDummy),PlanningHorizon))
    
#write out the shortest paths after running the roads for a scenario and then plug it into this:
#format for the CSV is I,J,T,PathLength
with open('RoadSchedule.csv') as RoadDataFromModel:
    for row in RoadDataFromModel:
        if SP[row[0]][row[1]][row[2]]==0:
            SP[i][j][t]=row[3]
        
for t in Time:
    model.addConstr(MST[t] == sum(SP[i][j][t]*Z[i,j,t] for i in NodesWithDummy for j in NodesWithDummy))
    model.addConstr(sum(Z[i,j,t] for i in NodesWithDummy for j in NodesWithDummy) == sum(F_n[i,t]for i in Nodes)+sum(F_l[e,t] for e in Edges)-1)
    for s in powerset(STE):
        if len(s)>=2:
            model.addConstr(sum(Z[i,j,t] for i in s for j in s)<=len(s)-1)
    for i in Nodes:
#        dropi = Nodes
#        dropi.remove(i)
       model.addConstr(sum(Z[i,j,t] for j in Nodes)>=F_n[i,t])
    for e in Edges:
        i = EdgeTracker[e][1][0]
        j = EdgeTracker[e][1][1]
        E = len(Nodes)+e
        model.addConstr(sum(Z[E,j,t] for j in NodesWithDummy) <= F_l[e,t])
#arbitrarily assigning node 13 to be the warehouse node
for t in Time:
    model.addConstr(sum(F_n[i,t]*5 for i in Nodes)+sum(F_l[e,t]*1 for e in Edges)+MST[t]<=8)

model.optimize()