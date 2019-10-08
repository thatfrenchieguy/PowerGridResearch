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
            if np.random.uniform(0,10)<=5:
                RoadGrid[i][j]['working']=False
            else:
                RoadGrid[i][j]['working']=True
        else:
            RoadGrid[i][j]['working']=True
for i in Nodes:
    for j in Nodes:
        if RoadGrid[i][j]['working']==False:
            print([i,j])
RoadGrid[0][3]['working']=False
RoadGrid[1][2]['working']=False
RoadGrid[1][26]['working']=False
RoadGrid[4][5]['working']=False
RoadGrid[5][13]['working']=False
RoadGrid[9][10]['working']=False
RoadGrid[9][13]['working']=False
RoadGrid[10][11]['working']=False
RoadGrid[10][12]['working']=False
RoadGrid[13][15]['working']=False
RoadGrid[14][16]['working']=False
RoadGrid[14][28]['working']=False
RoadGrid[16][17]['working']=False
RoadGrid[17][22]['working']=False
RoadGrid[18][21]['working']=False
RoadGrid[19][21]['working']=False
RoadGrid[19][23]['working']=False
RoadGrid[22][24]['working']=False
RoadGrid[22][25]['working']=False
RoadGrid[22][26]['working']=False
RoadGrid[24][27]['working']=False
RoadGrid[25][27]['working']=False
#define Variables
C = np.zeros((30,30))
for i in Nodes:
    for j in Nodes:
        if RoadGrid[i][j]['weight']<9000:
            C[i][j] = RoadGrid[i][j]['weight']
speed = 1/50
model = Model("mip1")
X = model.addVars(Nodes,Nodes,Time,vtype=GRB.BINARY, name = "X")
K = model.addVars(Nodes,Nodes,Time,vtype=GRB.BINARY, name = "K")
S = model.addVars(Nodes,Nodes,Time,vtype=GRB.CONTINUOUS, name = "S")
M=500
obj = model.setObjective(sum(t*sum(C[i][j]*(1-X[i,j,t]) for i in Nodes for j in Nodes)+.001*sum(S[i,j,t] for i in Nodes for j in Nodes) for t in Time),GRB.MINIMIZE)
for t in Time:
    for i in Nodes:
        for j in Nodes:
            model.addConstr(S[i,j,t] <= M*K[i,j,t]) 
            model.addConstr(S[i,j,t] >= RoadGrid[i][j]['weight']*speed*K[i,j,t])
            model.addConstr(S[i,j,t] >= (1-X[i,j,t])*8*RoadGrid[i][j]['weight']*speed - (1-K[i,j,t])*M)
    model.addConstr(sum(S[i,j,t] for i in Nodes for j in Nodes)<=8)
    for i in Nodes:
        model.addConstr(sum(K[i,j,t]for j in Nodes)-sum(K[j,i,t]for j in Nodes)==0)
    model.addConstr(sum(K[13,j,t] for j in Nodes)==1)
    PS = powerset(Nodes)
for s in PS:
 if len(s)<7:
  if len(s)>3:
   for t in Time:
    model.addConstr(sum(K[i,j,t] for i in s for j in s)<=len(s)-1)
for i in Nodes:
    for j in Nodes:
     for t in Time:
        model.addConstr(X[i,j,t] <= sum(K[i,j,v] for v in range(0,t))+int(RoadGrid[i][j]['working']))
setParam("NodefileStart", 5)
model.optimize()
#sytax for getting a variable in the output is variable[a,b].X to query it's value.
#do a sanity check:
for t in Time:
    for i in Nodes:
        for j in Nodes:
            if K[i,j,t].X >0:
                print([i,j,t,K[i,j,t].X])
with open ("RoadSchedule.csv",'w',newline = '') as OutputFile:
    cw = csv.writer(OutputFile, delimiter = ',' )
    for t in Time:
        for i in Nodes:
            for j in Nodes:
                if S[i,j,t].X != 0:
                    IJLength = S[i,j,t].X/speed
                    cw.writerow([i,j,t,IJLength])   
for i in Nodes:
    for j in Nodes:
        if RoadGrid[i][j]['working'] == False:
            print([i,j])