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
setParam("MIPGap", .005)            
###Random Scenario###
#RoadGrid[0][3]['working']=False
#RoadGrid[1][2]['working']=False
#RoadGrid[1][26]['working']=False
#RoadGrid[4][5]['working']=False
#RoadGrid[5][13]['working']=False
#RoadGrid[9][10]['working']=False
#RoadGrid[9][13]['working']=False
#RoadGrid[10][11]['working']=False
#RoadGrid[10][12]['working']=False
#RoadGrid[13][15]['working']=False
#RoadGrid[14][16]['working']=False
#RoadGrid[14][28]['working']=False
#RoadGrid[16][17]['working']=False
#RoadGrid[17][22]['working']=False
#RoadGrid[18][21]['working']=False
#RoadGrid[19][21]['working']=False
#RoadGrid[19][23]['working']=False
#RoadGrid[22][24]['working']=False
#RoadGrid[22][25]['working']=False
#RoadGrid[22][26]['working']=False
#RoadGrid[24][27]['working']=False
#RoadGrid[25][27]['working']=False
##Geographically oriented Scenario
#RoadGrid[20][21]['working']=False
#RoadGrid[18][23]['working']=False            
#RoadGrid[14][28]['working']=False
#RoadGrid[18][21]['working']=False
#RoadGrid[17][22]['working']=False
#RoadGrid[25][27]['working']=False
#RoadGrid[29][17]['working']=False
#RoadGrid[6][7]['working']=False
#RoadGrid[1][21]['working']=False
#RoadGrid[17][29]['working']=False
#RoadGrid[13][15]['working']=False
#RoadGrid[12][10]['working']=False     
#RoadGrid[9][13]['working']=False       
##IISE SCENARIO 2
RoadGrid[0][3]['working']=False
RoadGrid[3][4]['working']=False
RoadGrid[3][6]['working']=False
RoadGrid[4][5]['working']=False
RoadGrid[5][13]['working']=False
RoadGrid[7][21]['working']=False
RoadGrid[9][10]['working']=False
RoadGrid[9][15]['working']=False
RoadGrid[10][11]['working']=False
RoadGrid[10][12]['working']=False
RoadGrid[10][17]['working']=False
RoadGrid[12][13]['working']=False
RoadGrid[14][28]['working']=False
RoadGrid[14][29]['working']=False
RoadGrid[16][17]['working']=False
RoadGrid[17][22]['working']=False
RoadGrid[18][20]['working']=False
RoadGrid[18][21]['working']=False
RoadGrid[19][23]['working']=False
RoadGrid[22][26]['working']=False
RoadGrid[23][27]['working']=False
RoadGrid[25][26]['working']=False
##Random Generator
#for i in RoadGrid.nodes():
#    for j in range(i,len(RoadGrid.nodes())):
#      if RoadGrid.has_edge(i,j):
#       if RoadGrid[i][j]['weight'] <9000:
#        randbreak = np.random.uniform()
#        if randbreak <= .55:
#            print([i,j])
#            RoadGrid[i][j]['working']=False
#        else: 
#            RoadGrid[i][j]['working'] = True
for n in RoadGrid.nodes:
    for m in range(n,len(RoadGrid.nodes)):
        if RoadGrid.has_edge(n,m):
         if RoadGrid[n][m]['weight']<1000:
            if RoadGrid[n][m]['working']==False:
                print([n,m])
            
#define Variables
C = np.zeros((30,30))
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
M=50000
obj = model.setObjective(sum(t*sum(C[i][j]*(1-X[i,j,t]) for i in Nodes for j in Nodes)+10*D[t] for t in Time),GRB.MINIMIZE)
for t in Time:
    for i in Nodes:
        for j in Nodes:
            model.addConstr(S[i,j,t] <= M*K[i,j,t]) 
            model.addConstr(S[i,j,t] >= RoadGrid[i][j]['weight']*speed*K[i,j,t])
            model.addConstr(S[i,j,t] >= (1-X[i,j,t])*8*RoadGrid[i][j]['weight']*speed - (1-K[i,j,t])*M)
    model.addConstr(sum(S[i,j,t] for i in Nodes for j in Nodes)<=8)
    model.addConstr(D[t]<=3)
    for i in Nodes:
        model.addConstr(sum(K[i,j,t]for j in Nodes)-sum(K[j,i,t]for j in Nodes)==0)
    model.addConstr(sum(K[13,j,t] for j in Nodes)==1)
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

setParam("NodefileStart", 5)
model.optimize()
#sytax for getting a variable in the output is variable[a,b].X to query it's value.
#do a sanity check:
RoadLengths = np.zeros((len(Grid.nodes),len(Grid.nodes),len(Time)))
for i in Nodes:
        for j in Nodes:
             if RoadGrid[i][j]['working'] == True:
                    RoadLengths[i][j][0] = RoadGrid[i][j]['weight']
             else:
                    RoadLengths[i][j][0] = RoadGrid[i][j]['weight']*8
for t in range(1,len(Time)):
    for i in Nodes:
        for j in Nodes:
            if (sum(K[i,j,k].X for k in range(0,t-1))) >=1:
                RoadLengths[i][j][t] = RoadGrid[i][j]['weight']
            if (sum(K[i,j,k].X for k in range(0,t-1))) <=0:
                if RoadGrid[i][j]['working'] == True:
                    RoadLengths[i][j][t] = RoadGrid[i][j]['weight']
                else:
                    RoadLengths[i][j][t] = RoadGrid[i][j]['weight']*999

for t in Time:
    for i in Nodes:
        for j in Nodes:
            if K[i,j,t].X >0 and RoadGrid[i][j]['working'] ==False:
                print([i,j,t,K[i,j,t].X])
t=5                
sum(C[i][j]*(1-X[i,j,t].X) for i in Nodes for j in Nodes)

for i in Nodes:
    for t in Time:
        if (sum(K[i,j,t].X for j in Nodes)-sum(K[j,i,t].X for j in Nodes)) != 0:
            print([i,t])


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
K = model.addVars(Nodes,Nodes,Time, vtype = GRB.BINARY, lb = 0, ub=1, name = "K") #abuse total unimodularity to speed up the solving time if needed
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
#####SCENARIO OF BROKEN THINGS###
#Grid.node[27]['working']=False
#Grid.node[23]['working']=False
#Grid.node[18]['working']=False
#Grid.node[4]['working']=False
#Grid.node[7]['working']=False
#Grid.node[24]['working']=False
#Grid.node[15]['working']=False
#Grid[1][4][0]['working']=False
#Grid[4][6][0]['working']=False
#Grid[7][27][0]['working']=False
#Grid[24][25][0]['working']=False
#Grid[11][15][0]['working']=False
#Grid[1][3][0]['working']=False
#Grid[19][18][0]['working']=False
#Grid[9][22][0]['working']=False
#Grid[9][19][0]['working']=False

###END SCENARIO###            
###Geographic Scenario###
Grid.node[4]['working']=False
#
Grid.node[21]['working']=False
Grid.node[20]['working']=False
Grid.node[14]['working']=False
Grid.node[29]['working']=False
Grid.node[9]['working']=False
Grid[11][15][0]['working']=False
Grid[4][6][0]['working']=False
Grid[21][23][0]['working']=False
Grid[17][18][0]['working']=False
Grid[9][16][0]['working']=False
Grid[14][17][0]['working']=False
Grid[14][13][0]['working']=False
Grid[11][14][0]['working']=False
Grid[11][15][0]['working']=False
Grid[1][3][0]['working']=False
Grid[19][18][0]['working']=False

####IISE PAPER SCENARIO 2
#Grid.node[5]['working']=False
#Grid.node[14]['working']=False
#Grid.node[16]['working']=False
#Grid.node[18]['working']=False
#Grid.node[19]['working']=False
#Grid.node[21]['working']=False
#Grid.node[22]['working']=False
#Grid.node[23]['working']=False
#Grid.node[24]['working']=False
#Grid.node[26]['working']=False
#Grid[0][1][0]['working']=False
#Grid[1][4][0]['working']=False
#Grid[1][5][0]['working']=False
#Grid[3][5][0]['working']=False
#Grid[3][11][0]['working']=False
#Grid[5][6][0]['working']=False
#Grid[5][7][0]['working']=False
#Grid[5][9][0]['working']=False
#Grid[8][10][0]['working']=False
#Grid[9][19][0]['working']=False
#Grid[9][22][0]['working']=False
#Grid[11][12][0]['working']=False
#Grid[11][14][0]['working']=False
#Grid[14][17][0]['working']=False
#Grid[14][22][0]['working']=False
#Grid[17][18][0]['working']=False
#Grid[18][19][0]['working']=False
#Grid[20][21][0]['working']=False
#Grid[21][23][0]['working']=False
#Grid[23][24][0]['working']=False
#Grid[24][25][0]['working']=False
#Grid[24][26][0]['working']=False
#Grid[26][27][0]['working']=False
#Grid[28][29][0]['working']=False
##
#


##random generator
#for i in Grid.nodes():
#    for j in range(i,len(Grid.nodes())):
#      if Grid.has_edge(i,j,0):
#        randbreak = np.random.uniform()
#        if randbreak <= .5:
#            print([i,j])
#            Grid[i][j][0]['working']=False
#        else: 
#            Grid[i][j][0]['working'] = True
#for i in Grid.nodes():
#    randbreak = np.random.uniform()
#    if randbreak <= .25:
#            Grid.node[i]['working']=False
#    else:
#            Grid.node[i]['working']=True

##acounting for resilience 
#Grid.node[4]['working']=True
#Grid[1][5][0]['working']=True
#Grid[22][23][0]['working']=True
#Grid[0][1][0]['working']=True

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
STE = [13]
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
      model.addConstr(PG[i,t]-sum(PowerIJ[j,t] for j in originadj)+sum(PowerIJ[k,t] for k in destadj) == Grid.node[i]['load']*W_n[i,t])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:
    for t in Time:
        model.addConstr(PG[i,t]<=Grid.node[i]['productionmax']*W_n[i,t])
        model.addConstr(PG[i,t]>=0)
#constrain line limits
for e in Edges:
        for t in Time:
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e,t]*1.2)     
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0],t]*1.2)     
                model.addConstr(PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1],t]*1.2)
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e,t]*1.2)     
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0],t]*1.2)     
                model.addConstr(PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1],t]*1.2)                
           

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
    model.addConstr(MST[t] >= sum(SP[i][j][t]*K[i,j,t]*1/20 for i in Nodes for j in Nodes))
    for s in powerset(Nodes):
#        EdgesInS = []
#        for e in Edges:
#           if EdgeTracker[e][1][0] in s and EdgeTracker[e][1][1] in s:
#               EdgesInS.append(e)
        if len(s)>=7:
            break
        if len(s)>=3 and len(s)<=5:
            model.addConstr(sum(K[i,j,t] for i in s for j in s)<=len(s)-1)
    for i in Nodes:
       model.addConstr(K[i,i,t]==0)
       for j in Nodes:
           IncidentToI = []
           IncidentToJ = []
           for e in Edges:
               if EdgeTracker[e][1][0] == i or EdgeTracker[e][1][1] ==i:
                   IncidentToI.append(e)
               if EdgeTracker[e][1][0] == j or EdgeTracker[e][1][1] ==j:
                   IncidentToJ.append(e)
#           if i!=13:
           model.addConstr(sum(K[i,j,t] for j in Nodes)>=F_n[i,t])
           model.addConstr(sum(K[i,j,t] for j in Nodes) - sum(K[j,i,t] for j in Nodes) ==0)
    for e in Edges:
        End1 = EdgeTracker[e][1][0]
        End2 = EdgeTracker[e][1][1]
        model.addConstr(sum(K[End1,j,t] for j in Nodes)+sum(K[End2,j,t] for j in Nodes)>=F_l[e,t])
    for i in Nodes:
        if Grid.node[i]['working']==True:
            model.addConstr(F_n[i,t]==0)
    for e in Edges:
        if Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['working'] == True:
            model.addConstr(F_l[e,t] == 0)
    model.addConstr(sum(K[13,j,t] for j in Nodes) ==1)
for t in Time:
    model.addConstr(sum(F_n[i,t]*5 for i in Nodes)+sum(F_l[e,t]*1 for e in Edges)+MST[t]<=12)
#    model.addConstr(Delta[t]<=3)
setParam("MIPGap", .03)
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
        t = 4
#        for t in Time:
        if K[i,j,t].X != 0:
                print([i,j,K[i,j,t].X])
#t=4
#for i in Edges:
#                print(PowerIJ[i,t].X)              
for t in Time:          
    print(sum((1-W_n[i,t].X)*Grid.node[i]['load'] for i in Nodes ))

#    