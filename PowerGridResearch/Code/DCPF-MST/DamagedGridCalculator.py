# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 11:02:23 2020

@author: BrianFrench
"""
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from gurobipy import *
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = list(range(0,len(PowerSub.edges)))
Nodes = list(range(0,len(Grid.nodes)))
model = Model("mip1")
#define Variables
#Decision Variables
PG = model.addVars(Nodes,vtype=GRB.CONTINUOUS, name = "PG",lb = 0)
##State Variables
W_l = model.addVars(Edges, vtype = GRB.BINARY, name = "W_l")
W_n = model.addVars(Nodes, vtype = GRB.BINARY, lb = 0, ub=1, name = "W_n")
Theta = model.addVars(Nodes, vtype = GRB.CONTINUOUS, name = "Theta")
PowerIJ = model.addVars(Edges, vtype = GRB.CONTINUOUS, name = "PowerIJ")
Shed = model.addVars(Nodes, vtype = GRB.CONTINUOUS, name = "Shed")
#default everything to working
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True

#######   RANDOM SCENARIO         

for i in Grid.nodes:
    Grid.node[i]['working']=True
    for j in Grid.nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True
####END SCENARIO###            
###Random Scenario####
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
##Geographic Scenario###
#Grid.node[4]['working']=False
#Grid.node[21]['working']=False
#Grid.node[20]['working']=False
#Grid.node[14]['working']=False
#Grid.node[29]['working']=False
#Grid.node[9]['working']=False
#Grid[4][6][0]['working']=False
#Grid[21][23][0]['working']=False
#Grid[17][18][0]['working']=False
#Grid[9][16][0]['working']=False
#Grid[14][17][0]['working']=False
#Grid[14][13][0]['working']=False
#Grid[11][14][0]['working']=False
#Grid[11][15][0]['working']=False
#Grid[1][3][0]['working']=False
#Grid[19][18][0]['working']=False
####RESILIENCE TEST#####
Grid.node[4]['working']=False
Grid.node[7]['working']=False
Grid[22][23][0]['working']=False           
Grid[5][9][0]['working']=False
Grid[23][24][0]['working']=False     
Grid[14][17][0]['working']=False       
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
######Geographic Scenario for 57 bus###
#Grid.node[4]['working']=False
#Grid.node[11]['working']=False
#Grid.node[28]['working']=False
#Grid.node[21]['working']=False
#Grid.node[20]['working']=False
#Grid.node[14]['working']=False
#Grid.node[29]['working']=False
#Grid.node[9]['working']=False
#Grid.node[31]['working']=False
#Grid[3][4][0]['working']=False ###
#Grid[5][7][0]['working']=False
#Grid[34][35][0]['working']=False ###
#Grid[54][8][0]['working']=False
#Grid[38][56][0]['working']=False
#
#Grid[12][48][0]['working']=False
#Grid[39][55][0]['working']=False
#Grid[22][23][0]['working']=False
#Grid[8][11][0]['working']=False
#Grid[11][15][0]['working']=False
#Grid[21][37][0]['working']=False
#Grid[23][24][0]['working']=False
#Grid[24][29][0]['working']=False
#Grid[31][33][0]['working']=False
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


obj = model.setObjective(sum(Shed[i] for i in Nodes),GRB.MINIMIZE)


#impose phase angle constraints

M=10000

model.addConstr(Theta[0] == 0)
for i in Nodes:
    for j in Nodes:
         for k in range(0,len(EdgeTracker)):
            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
#                    print([i,j])
                    model.addConstr(PowerIJ[k] >= 250*Grid[i][j][0]['Sus']*(Theta[j]-Theta[i])-50*M*W_l[k])
                    model.addConstr(PowerIJ[k] <= M*W_l[k])
                    model.addConstr(PowerIJ[k] <= 250*Grid[i][j][0]['Sus']*(Theta[j]-Theta[i]))

for i in Nodes:

      originadj = []
      destadj = []
      for k in Edges:
          if EdgeTracker[k][1][0] == i:
              originadj.append(k)
          if EdgeTracker[k][1][1]==i:
              destadj.append(k)
      model.addConstr(PG[i]-sum(PowerIJ[j] for j in originadj)+sum(PowerIJ[k] for k in destadj) == Grid.node[i]['load']-Shed[i])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:

        model.addConstr(PG[i]<=Grid.node[i]['productionmax']*W_n[i]*1)
        model.addConstr(Shed[i]<=Grid.node[i]['load'])
        model.addConstr(Shed[i]>=0)
        model.addConstr(PG[i]>=0)
#constrain line limits
for e in Edges:
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e]*1.61)     
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]]*1.61)     
                model.addConstr(PowerIJ[e]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]]*1.61)
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_l[e]*1.61)     
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][0]]*1.61)     
                model.addConstr(PowerIJ[e]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*W_n[EdgeTracker[e][1][1]]*1.61)                
           

#define workingness
for i in Nodes:
    model.addConstr(W_n[i] <= Grid.node[i]['working'])
for e in Edges:
        model.addConstr(W_l[e]<=int(EdgeStartingStatus[e]))
model.optimize()
#
#for i in Edges:
#                print(PowerIJ[i].X)  