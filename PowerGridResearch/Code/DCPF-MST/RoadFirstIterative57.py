# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:45:12 2019

@author: BrianFrench
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May  6 14:31:19 2019

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
Grid = nx.read_gml("Bus57WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
demsum = 0
gensum = 0
for n in Grid.nodes:
    demsum+=Grid.node[n]['load']
    gensum += Grid.node[n]['productionmax']
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 8 #this is measured in shifts
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
for i in range(0,len(Grid.nodes)):
 for j in Nodes:
    if Grid.has_edge(i,j,1):
            RoadGrid[i][j]['working']=True
    else:
        RoadGrid[i][j]['working']=True
  
###Random Scenario###
#        
RoadGrid[0][12]['working']=False
RoadGrid[1][14]['working']=False
RoadGrid[2][44]['working']=False
RoadGrid[2][23]['working']=False
RoadGrid[3][33]['working']=False
RoadGrid[3][6]['working']=False
RoadGrid[4][14]['working']=False
RoadGrid[4][17]['working']=False
RoadGrid[4][23]['working']=False
RoadGrid[5][17]['working']=False
RoadGrid[6][3]['working']=False
RoadGrid[6][51]['working']=False
RoadGrid[6][27]['working']=False
RoadGrid[7][27]['working']=False
RoadGrid[8][42]['working']=False
RoadGrid[9][10]['working']=False
RoadGrid[9][49]['working']=False
RoadGrid[10][22]['working']=False
RoadGrid[10][49]['working']=False
RoadGrid[11][26]['working']=False
RoadGrid[12][16]['working']=False
RoadGrid[13][43]['working']=False
RoadGrid[13][52]['working']=False
RoadGrid[13][43]['working']=False
RoadGrid[14][17]['working']=False
RoadGrid[15][16]['working']=False
RoadGrid[16][36]['working']=False
RoadGrid[19][33]['working']=False
RoadGrid[19][44]['working']=False
RoadGrid[21][23]['working']=False
RoadGrid[21][47]['working']=False
RoadGrid[22][29]['working']=False
RoadGrid[23][34]['working']=False
RoadGrid[24][26]['working']=False
RoadGrid[24][45]['working']=False
RoadGrid[25][29]['working']=False
RoadGrid[27][51]['working']=False
RoadGrid[28][36]['working']=False
RoadGrid[29][49]['working']=False
RoadGrid[30][32]['working']=False
RoadGrid[30][51]['working']=False
RoadGrid[31][52]['working']=False
RoadGrid[33][53]['working']=False
RoadGrid[34][53]['working']=False
RoadGrid[35][46]['working']=False
RoadGrid[37][40]['working']=False
RoadGrid[38][48]['working']=False
RoadGrid[39][50]['working']=False
RoadGrid[41][44]['working']=False
RoadGrid[41][53]['working']=False
RoadGrid[42][55]['working']=False
RoadGrid[43][45]['working']=False
RoadGrid[46][56]['working']=False
RoadGrid[47][51]['working']=False

###Generate Random Scenario  
#for i in RoadGrid:
#    for j in RoadGrid:
#        if RoadGrid.has_edge(i,j):
#            if RoadGrid[i][j]['weight']<500:
#                print([i,j])
#for i in RoadGrid.nodes():
#    for j in range(i,len(RoadGrid.nodes())):
#      if RoadGrid.has_edge(i,j):
#        randbreak = np.random.uniform()
#        if randbreak <= .6:
#            print([i,j])
#            RoadGrid[i][j]['working']=False
#        else: 
#            RoadGrid[i][j]['working'] = True

#define Variables
C = np.zeros((57,57))
for i in Nodes:
    for j in Nodes:
        if RoadGrid[i][j]['weight']<9000:
            C[i][j] = RoadGrid[i][j]['weight']
speed = 1/20
model = Model("mip1")
X = model.addVars(Nodes,Nodes,Time,vtype=GRB.BINARY, name = "X")
K = model.addVars(Nodes,Nodes,Time,vtype=GRB.BINARY, name = "K")
S = model.addVars(Nodes,Nodes,Time,vtype=GRB.CONTINUOUS, name = "S")
D = model.addVars(Time, vtype = GRB.CONTINUOUS, name = "D")
M=5000
obj = model.setObjective(sum(t*sum(C[i][j]*(1-X[i,j,t]) for i in Nodes for j in Nodes) for t in Time),GRB.MINIMIZE)
for t in Time:
    for i in Nodes:
        for j in Nodes:
            model.addConstr(S[i,j,t] <= M*K[i,j,t]) 
            model.addConstr(S[i,j,t] >= RoadGrid[i][j]['weight']*speed*K[i,j,t])
            model.addConstr(S[i,j,t] >= (1-X[i,j,t])*8*RoadGrid[i][j]['weight']*speed - (1-K[i,j,t])*M)
    model.addConstr(sum(S[i,j,t] for i in Nodes for j in Nodes)<=12)

    for i in Nodes:
        model.addConstr(sum(K[i,j,t]for j in Nodes)-sum(K[j,i,t]for j in Nodes)==0)
    model.addConstr(sum(K[38,j,t] for j in Nodes)==1)
    PS = powerset(Nodes)
for s in PS:
 if len(s)>5:
     break
 if len(s)<4:
  if len(s)>1:
   for t in Time:
    model.addConstr(sum(K[i,j,t] for i in s for j in s)<=len(s)-1)
for i in Nodes:
    for j in Nodes:
     for t in Time:
        model.addConstr(X[i,j,t] <= sum(K[i,j,v] for v in range(0,t))+int(RoadGrid[i][j]['working']))
#        
#for i in Nodes:
#    for j in Nodes:
#        if int(RoadGrid[i][j]['working']) != 0 and int(RoadGrid[i][j]['working']) != 1:
#            print(int(RoadGrid[i][j]['working']))

setParam("MIPGap", .05)
model.optimize()
#sytax for getting a variable in the output is variable[a,b].X to query it's value.
#do a sanity check:
RoadLengths = np.zeros((len(Grid.nodes),len(Grid.nodes),len(Time)))
#for i in Nodes:
#        for j in Nodes:
#             if RoadGrid[i][j]['working'] == True:
#                    RoadLengths[i][j][0] = RoadGrid[i][j]['weight']
#             else:
#                    RoadLengths[i][j][0] = RoadGrid[i][j]['weight']*8
for t in range(0,len(Time)):
    for i in Nodes:
        for j in Nodes:
            if (sum(K[i,j,k].X for k in range(0,t-1))) >=1:
                RoadLengths[i][j][t] = RoadGrid[i][j]['weight']
            if (sum(K[i,j,k].X for k in range(0,t-1))) <=0:
                if RoadGrid[i][j]['working'] == True:
                    RoadLengths[i][j][t] = RoadGrid[i][j]['weight']
                else:
                    RoadLengths[i][j][t] = RoadGrid[i][j]['weight']*8

for t in Time:
    for i in Nodes:
        for j in Nodes:
            if K[i,j,t].X >0 and RoadGrid[i][j]['working'] ==False:
                print([i,j,t,K[i,j,t].X])
t=2                
sum(C[i][j]*(1-X[i,j,t].X) for i in Nodes for j in Nodes)

for i in Nodes:
    for t in Time:
        if (sum(K[i,j,t].X for j in Nodes)-sum(K[j,i,t].X for j in Nodes)) != 0:
            print([i,t])


SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 8 #this is measured in shifts
ShiftLength = 8 #in Hours
#Define sets to be used in optimiation
PowerSub = nx.read_gml("Bus57WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = list(range(0,len(PowerSub.edges)))
Nodes = list(range(0,57))
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
Shed = model.addVars(Nodes,Time, vtype = GRB.CONTINUOUS, name = "Shed")
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
tour = [[13,5],[5,4],[4,3],[3,6],[6,7],[7,21],[21,1],[1,17],[17,10],[10,9],[9,15],[15,13]]
tourdraw = []
for i in x:
    pos.append((x[i],y[i]))
for e in Grid.edges:
    if e[2]==0:
        power.append(e)
    if e[2]==1:
        road.append(e)
for t in tour:
    tourdraw.append((t[0],t[1],1))
        
nx.draw_networkx_nodes(Grid, pos, label=True)
nx.draw_networkx_labels(Grid, pos)
#nx.draw_networkx_edges(Grid, pos, edgelist = power, edge_color = "g", width = 2, alpha =.7)
nx.draw_networkx_edges(Grid, pos, edgelist = road, edge_color = 'r', width = 2, alpha = .3)
nx.draw_networkx_edges(Grid, pos, edgelist = tourdraw, edge_color = 'b', width = 4, alpha = 1)
#
plt.axis('off')
plt.show()
#######   RANDOM SCENARIO         

for i in Grid.nodes:
    Grid.node[i]['working']=True
    for j in Grid.nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True
####END SCENARIO###            
####Geographic Scenario###
Grid.node[4]['working']=False
Grid.node[11]['working']=False
Grid.node[28]['working']=False
Grid.node[21]['working']=False
Grid.node[20]['working']=False
Grid.node[14]['working']=False
Grid.node[29]['working']=False
Grid.node[9]['working']=False
Grid.node[31]['working']=False
Grid[3][4][0]['working']=False ###
Grid[5][7][0]['working']=False
Grid[34][35][0]['working']=False ###
Grid[54][8][0]['working']=False
Grid[38][56][0]['working']=False

Grid[12][48][0]['working']=False
Grid[39][55][0]['working']=False
Grid[22][23][0]['working']=False
Grid[8][11][0]['working']=False
Grid[11][15][0]['working']=False
Grid[21][37][0]['working']=False
Grid[23][24][0]['working']=False
Grid[24][29][0]['working']=False
Grid[31][33][0]['working']=False
##random generator
#for i in Grid.nodes():
#    for j in range(i,len(Grid.nodes())):
#      if Grid.has_edge(i,j,0):
#        randbreak = np.random.uniform()
#        if randbreak <= .4:
#            print([i,j])
#            Grid[i][j][0]['working']=False
#        else: 
#            Grid[i][j][0]['working'] = True
#for i in Grid.nodes():
#    randbreak = np.random.uniform()
#    if randbreak <= .2:
#            Grid.node[i]['working']=False
#    else:
#            Grid.node[i]['working']=True            
#            
setParam("MIPGap", .03)
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
STE = [38]
for i in range(len(Grid.nodes())):
    if Grid.node[i]['working']==False:
        STE.append(i)
for j in range(len(EdgeStartingStatus)):
    if EdgeStartingStatus[j]==0 and EdgeTracker[j][1][0] not in STE:
        STE.append(EdgeTracker[j][1][0])
    if EdgeStartingStatus[j]==0 and EdgeTracker[j][1][1] not in STE:
        STE.append(EdgeTracker[j][1][1])
###End STE building###


obj = model.setObjective(sum(sum(Shed[i,t] for i in Nodes) for t in Time),GRB.MINIMIZE)


#impose phase angle constraints


M=10000
for t in Time:
    model.addConstr(Theta[0,t] == 0)
for i in Nodes:
    for j in Nodes:
        for t in Time:
         for k in range(0,len(EdgeTracker)):
            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
#                    print([i,j])
                    model.addConstr(PowerIJ[k,t] >= 250*Grid[i][j][0]['Sus']*(Theta[j,t]-Theta[i,t])-5*M*W_l[k,t])
                    model.addConstr(PowerIJ[k,t] <= M*W_l[k,t])
                    model.addConstr(PowerIJ[k,t] <= 250*Grid[i][j][0]['Sus']*(Theta[j,t]-Theta[i,t]))
#                    model.addConstr(PowerIJ[k,t] <= 1.05*500*Grid[i][j][0]['Sus']*(Theta[j,t]-Theta[i,t])*W_l[k,t])
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
      model.addConstr(PG[i,t]-sum(PowerIJ[j,t] for j in originadj)+sum(PowerIJ[k,t] for k in destadj) == Grid.node[i]['load']-Shed[i,t])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:
    for t in Time:
        model.addConstr(PG[i,t]<=Grid.node[i]['productionmax']*W_n[i,t]*1.5)
        model.addConstr(Shed[i,t]<=Grid.node[i]['load'])
        model.addConstr(Shed[i,t]>=0)
        model.addConstr(PG[i,t]>=0)
#constrain line limits
for e in Edges:
        for t in Time:
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e,t]*1.61)     
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0],t]*1.61)     
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1],t]*1.61)
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e,t]*1.61)     
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0],t]*1.61)     
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1],t]*1.61)                
 
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
SP = np.zeros((len(Nodes), len(Nodes), len(Time)))
ArrayOfRoadGrids = []
for t in Time:
    RoadGrid = nx.Graph()
    RoadGrid.add_nodes_from(Grid)
    for i in Nodes:
        for j in Nodes:
            RoadGrid.add_edge(i,j,weight = RoadLengths[i][j][t])
    ArrayOfRoadGrids.append(RoadGrid)


for i in Nodes:
    for j in Nodes:
     for t in Time:
        SP[i][j][t] = nx.shortest_path_length(ArrayOfRoadGrids[t], source = i, target = j, weight='weight')
for t in Time:
    model.addConstr(MST[t] >= sum(SP[i][j][t]*Z[i,j,t]*1/10 for i in Nodes for j in Nodes))
    model.addConstr(sum(Z[i,j,t] for i in Nodes for j in Nodes) == sum(F_n[i,t]for i in Nodes)+sum(F_l[e,t] for e in Edges)-sum(F_n[i,t]*sum(F_l[e,t]*EdgeIncidence[n][e] for e in Edges) for i in Nodes)-1)
    for s in powerset(STE):
        if len(s)>=5:
            break
        if len(s)>=1 and len(s)<=4:
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

for t in Time:
    model.addConstr(sum(F_n[i,t]*5 for i in Nodes)+sum(F_l[e,t]*1 for e in Edges)+MST[t]<=12)
#    model.addConstr(Delta[t]<=3)

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
##for i in Edges:
##        for t in Time:
#            if PowerIJ[i,t].X != 0:
#                print(PowerIJ[i,t].X)              
for t in Time:          
    print(sum(Shed[i,t].X for i in Nodes ))
#for t in Time:
##    print(sum(PG[n,t].X for n in Grid.nodes))
#    for n in Grid.nodes:
#        if Grid.node[n]['load']>0 and W_n[n,t].X ==0:
#            print([n,t,Grid.node[n]['load']])
#for i in Grid.nodes:
#    for j in Grid.nodes:
#        if Z[i,j,t].X != 0:
#            print([i,j])