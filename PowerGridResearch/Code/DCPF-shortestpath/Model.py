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
import pyomo.environ as pe
#initialize graph from file
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 12 #this is measured in shifts
ShiftLength = 8 #in Hours
#Define sets to be used in optimiation
Nodes = pe.Set(initialize= range(0,30))
Time = pe.Set(initialize = range(0,PlanningHorizon))
model = pe.ConcreteModel()
#define Variables
##Decision Variables
model.PG = pe.Var(Nodes,Time)
model.F_l = pe.Var(Nodes,Nodes,Time, domain=pe.Binary)
model.F_n = pe.Var(Nodes,Time, domain = pe.Binary)
##State Variables
model.W_l = pe.Var(Nodes,Nodes,Time, domain = pe.Binary)
model.W_n = pe.Var(Nodes, Time, domain = pe.Binary)
model.Theta = pe.Var(Nodes,Time)
model.PowerIJ = pe.Var(Nodes,Nodes,Time, domain = pe.Reals)

#just comment out the not needed scenario
##sets everything to working
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')

#Scenario 1
Grid.node[10]['working']=False
Grid.node[2]['working']=False
Grid.node[11]['working']=False
Grid.node[22]['working']=False
Grid.node[13]['working']=False
#damage to lines comes from 20% chance simulated then hardcoded for consistency
Grid[0][1][0]['working']=False
Grid[1][4][0]['working']=False
Grid[9][16][0]['working']=False
Grid[9][20][0]['working']=False
Grid[11][15][0]['working']=False
Grid[13][14][0]['working']=False
Grid[15][16][0]['working']=False
Grid[24][25][0]['working']=False
Grid[9][19][0]['working']=False
Grid[14][17][0]['working']=False
Grid[26][29][0]['working']=False
Grid[29][28][0]['working']=False

##Constant Sets
model.obj = pe.Objective(expr = sum((1-model.W_n[i,t])*Grid.node[i]['load'] for i in Nodes for t in Time))

#impose phase angle constraints
M=1000
model.PAcons = pe.ConstraintList()
for i in Nodes:
    for j in range(0,i+1):
        for t in Time:
            if Grid.has_edge(i,j,0):
                if 'Sus' in Grid[i][j][0]:
                    model.PAcons.add(model.PowerIJ[i,j,t] == model.W_l[i,j,t]*Grid[i][j][0]['Sus']*(model.Theta[i,t]-model.Theta[j,t]))
            else:
                model.PAcons.add(model.PowerIJ[i,j,t] == 0)
            model.PAcons.add(model.Theta[i,t]<=3.14)
            model.PAcons.add(model.Theta[j,t]>=0)
    for j in range(i+1,len(Nodes)):
        for t in Time:
            model.PAcons.add(model.PowerIJ[i,j,t]==0)
#impose power balance constraints
model.PBcons = pe.ConstraintList()
for i in Nodes:
    for t in Time:
      model.PBcons.add(model.PG[i,t]-sum(model.PowerIJ[i,j,t] for j in Nodes)+sum(model.PowerIJ[j,i,t] for j in Nodes) == Grid.node[i]['load']*model.W_n[i,t])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:
    for t in Time:
        model.PBcons.add(model.PG[i,t]<=Grid.node[i]['productionmax']*model.W_n[i,t])
        model.PBcons.add(model.PG[i,t]>=0)
#constrain line limits
model.LineLoadcons = pe.ConstraintList()
for i in Nodes:
    for j in range(0,i+1):
        for t in Time:
            if Grid.has_edge(i,j,0):
                #model.LineLoadcons.add(model.PowerIJ[i,j,t]<=Grid[i][j][0]['capacity']*model.W_l[i,j,t])     
                #model.LineLoadcons.add(model.PowerIJ[i,j,t]<=Grid[i][j][0]['capacity']*model.W_n[i,t])     
                #model.LineLoadcons.add(model.PowerIJ[i,j,t]<=Grid[i][j][0]['capacity']*model.W_n[j,t])
                #model.LineLoadcons.add(model.PowerIJ[i,j,t]>=-1*Grid[i][j][0]['capacity']*model.W_l[i,j,t]+(-1)*Grid[i][j][0]['capacity']*model.W_l[j,i,t])     
                #model.LineLoadcons.add(model.PowerIJ[i,j,t]>=-1*Grid[i][j][0]['capacity']*model.W_n[i,t])     
                #model.LineLoadcons.add(model.PowerIJ[i,j,t]>=-1*Grid[i][j][0]['capacity']*model.W_n[j,t])
                a=1
           

#define workingness
model.Working = pe.ConstraintList()
for i in Nodes:
    model.Working.add(model.W_n[i,0] == Grid.node[i]['working'])
    for j in range(0,i+1):
        if Grid.has_edge(i,j,0):
         model.Working.add(model.W_l[i,j,0]==Grid[i][j][0]['working'])
    for t in range(1,len(Time)):
        model.Working.add(model.W_n[i,t]<=sum(model.F_n[i,g] for g in range(0,t-1))+Grid.node[i]['working'])
        for j in range(0,i+1):
          if Grid.has_edge(i,j,0):
            model.Working.add(model.W_l[i,j,t]<=sum(model.F_l[i,j,g] for g in range(0,t-1))+Grid[i][j][0]['working'])     
#schedule restriction so that nothing gets double fixed
for i in Nodes:
    model.Working.add(sum(model.F_n[i,t]for t in Time)<=1)
    for j in range(0,i+1):
        if Grid.has_edge(i,j,0):
            model.Working.add(sum(model.F_l[i,j,t] for t in Time)<=1)            
#build shortest path matrix
SP = np.zeros(len(Nodes))

RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
#arbitrarily assigning node 13 to be the warehouse node
##Assumption is that 30 length can be traveled per hour
for i in Nodes:        
        SP[i] = nx.shortest_path_length(RoadGrid,source = i,target = 13,weight = 'weight')
model.Scheduling = pe.ConstraintList()
for t in Time:
    model.Scheduling.add(sum(model.F_n[i,t]*5+model.F_n[i,t]*SP[i]*2*(1/50) for i in Nodes)+sum(model.F_l[i,j,t]*1+model.F_l[i,j,t]*min(SP[i],SP[j])*2*(1/50)for i in Nodes for j in Nodes)<=8)

solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)    

for i in Nodes:
    for j in Nodes:
     if model.PowerIJ[i,j,0].value>0:
      print([i,j,model.PowerIJ[i,j,0].value])
for t in Time:
 for i in Nodes:
  if model.F_n[i,t].value >0:
    print(i,t, model.F_n[i,t].value)
    