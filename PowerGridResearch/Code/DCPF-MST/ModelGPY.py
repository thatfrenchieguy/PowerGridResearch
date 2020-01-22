# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 15:49:25 2019

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
Z = model.addVars(Nodes,Nodes,Time, vtype = GRB.BINARY, lb = 0, ub=1, name = "Z") #abuse total unimodularity to speed up the solving time if needed
##State Variables
W_l = model.addVars(Edges,Time, vtype = GRB.BINARY, name = "W_l")
W_n = model.addVars(Nodes, Time, vtype = GRB.BINARY, name = "W_n")
Theta = model.addVars(Nodes,Time, vtype = GRB.CONTINUOUS, name = "Theta")
PowerIJ = model.addVars(Edges,Time, vtype = GRB.CONTINUOUS, name = "PowerIJ")
MST = model.addVars(Time, vtype = GRB.CONTINUOUS, lb=0, name = "MST")
Delta = model.addVars(Time, vtype = GRB.CONTINUOUS, lb =0, name = "Delta")
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
#nx.draw_networkx_edges(Grid, pos, edgelist = power, edge_color = "g", width = 2, alpha =.7)
nx.draw_networkx_edges(Grid, pos, edgelist = road, edge_color = 'r', width = 2, alpha = .7)
#
plt.axis('off')
plt.show()
#######            
#######            
#######   RANDOM SCENARIO         
#####SCENARIO OF BROKEN THINGS###
#Grid.node[27]['working']=False
#Grid.node[23]['working']=False
#Grid.node[18]['working']=False
#Grid.node[4]['working']=False
#Grid.node[7]['working']=False
#Grid.node[24]['working']=False
##Grid.node[15]['working']=False
#Grid[1][4][0]['working']=False
#Grid[4][6][0]['working']=False
#Grid[7][27][0]['working']=False
#Grid[24][25][0]['working']=False
#Grid[11][15][0]['working']=False
#Grid[1][3][0]['working']=False
#Grid[19][18][0]['working']=False
#Grid[9][22][0]['working']=False
#Grid[9][19][0]['working']=False

####END SCENARIO###            
####Geographic Scenario###
Grid.node[21]['working']=False
Grid.node[20]['working']=False
Grid.node[16]['working']=False
Grid.node[14]['working']=False
Grid.node[29]['working']=False
Grid.node[9]['working']=False
Grid[11][15][0]['working']=False
Grid[4][6][0]['working']=False
Grid[21][23][0]['working']=False
Grid[17][18][0]['working']=False
Grid[9][22][0]['working']=False
Grid[9][16][0]['working']=False
Grid[14][17][0]['working']=False
Grid[14][13][0]['working']=False
Grid[28][29][0]['working']=False
Grid[11][14][0]['working']=False

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
                    
#construct incidence matrix of edges/nodes for building 
EdgeIncidence = np.zeros((len(Nodes),len(Edges)))
for n in Nodes:
    for e in Edges:
        if EdgeTracker[e][1][0] == n:
            EdgeIncidence[n][e] = 1
        if EdgeTracker[e][1][1] == n:
            EdgeIncidence[n][e] = 1
###Build broken elements into a list for STE constraints####
STE = []
for i in range(len(Grid.nodes())):
    if Grid.node[i]['working']==False:
        STE.append(i)
for j in range(len(EdgeStartingStatus)):
    if EdgeStartingStatus[j]==0 and EdgeTracker[j][1][0] not in STE:
        STE.append(EdgeTracker[j][1][0])
    if EdgeStartingStatus[j]==0 and EdgeTracker[j][1][1] not in STE:
        STE.append(EdgeTracker[j][1][1])
###End STE building###


obj = model.setObjective(sum(sum((1-W_n[i,t])*Grid.node[i]['load'] for i in Nodes)+20*Delta[t] for t in Time),GRB.MINIMIZE)


#impose phase angle constraints

M=10000
for t in Time:
    model.addConstr(Theta[0,t] == 0)
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
        model.addConstr(W_n[i,t]<=sum(F_n[i,g] for g in range(0,t))+int(Grid.node[i]['working']))
for e in Edges:
    for t in Time:
        model.addConstr(W_l[e,t]<=sum(F_l[e,g] for g in range(0,t))+int(EdgeStartingStatus[e]))
        
#schedule restriction so that nothing gets double fixed
for i in Nodes:
    model.addConstr(sum(F_n[i,t]for t in Time)<=1)   
for e in Edges:
    model.addConstr(sum(F_l[e,t]for t in Time)<=1)         
#build shortest path matrix
SP = np.zeros((len(Nodes), len(Nodes)))
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
for i in Nodes:
    for j in Nodes:
        SP[i][j] = nx.shortest_path_length(RoadGrid, source = i, target = j, weight='weight')
for t in Time:
    model.addConstr(MST[t] >= sum(SP[i][j]*Z[i,j,t]*1/10 for i in Nodes for j in Nodes))
    model.addConstr(sum(Z[i,j,t] for i in Nodes for j in Nodes) >= sum(F_n[i,t]for i in Nodes)+sum(F_l[e,t] for e in Edges)-sum(F_n[i,t]*sum(F_l[e,t]*EdgeIncidence[n][e] for e in Edges) for i in Nodes))
    for s in powerset(STE):
        if len(s)>=2 and len(s)<=8:
            model.addConstr(sum(Z[i,j,t] for i in s for j in s)<=len(s)-1)
    for i in Nodes:
       model.addConstr(Z[i,i,t]==0)
       for j in Nodes:
           IncidentToI = []
           IncidentToJ = []
           for e in Edges:
               if EdgeTracker[e][1][0] == i or EdgeTracker[e][1][1] ==i:
                   IncidentToI.append(e)
               if EdgeTracker[e][1][0] == j or EdgeTracker[e][1][1] ==j:
                   IncidentToJ.append(e)
#           if i!=13:
           model.addConstr(Z[i,j,t]<=F_n[i,t]+sum(F_l[e,t] for e in IncidentToI))
           model.addConstr(Z[i,j,t]<=F_n[j,t]+sum(F_l[e,t] for e in IncidentToJ))
    for i in Nodes:
        if Grid.node[i]['working']==True:
            model.addConstr(F_n[i,t]==0)
    for e in Edges:
        if Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['working'] == True:
            model.addConstr(F_l[e,t] == 0)
#        model.addConstr(sum(Z[o,j,t] for j in Nodes)+sum(Z[j,d,t] for j in Nodes) >= F_l[e,t])
#arbitrarily assigning node 13 to be the warehouse node
#for t in Time:
#    model.addConstr(sum(Z[13,j,t] for j in Nodes)>=1)

for t in Time:

    model.addConstr(sum(F_n[i,t]*5 for i in Nodes)+sum(F_l[e,t]*1 for e in Edges)+MST[t]<=8)

#model.addConstr(F_n[4,0] ==1)
##model.addConstr(F_l[3,0]==1)
##model.addConstr(F_l[17,1]>=1)
##model.addConstr(F_l[24,1]>=1)
##model.addConstr(F_l[2,1]>=1)
##model.addConstr(F_l[35,2]>=1)
#model.addConstr(F_n[7,2]>=1)
#model.addConstr(F_n[23,3]==1)
##model.addConstr(F_l[8,3]>=1)
#model.addConstr(F_n[24,4]==1)
##model.addConstr(F_n[18,4]>=1)









model.optimize()

for t in Time:
    for n in Nodes:
        if F_n[n,t].X != 0:
            print(["N",n,t])
            print(F_n[n,t].X)
    for e in Edges:
        if F_l[e,t].X != 0:
            print(["L",e,t])
            print(F_l[e,t].X)

for i in Nodes:
    for j in Nodes:
        t = 3
#        for t in Time:
        if Z[i,j,t].X != 0:
                print([i,j,Z[i,j,t].X])
#for i in Edges:
#        for t in Time:
#            if PowerIJ[i,t].X != 0:
#                print(PowerIJ[i,t].X)
                
for t in Time:
    for n in Nodes:
        if W_n[n,t].X == 0:
            print([n,t])

t=0            
for t in Time:
    print(sum((1-W_n[i,t].X)*Grid.node[i]['load'] for i in Nodes ))
for i in Nodes:
    
    print([i,W_n[i,t].X])
    
