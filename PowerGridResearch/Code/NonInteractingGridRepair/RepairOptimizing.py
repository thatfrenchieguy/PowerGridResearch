# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 11:47:53 2018

@author: BrianFrench
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import pyomo.environ as pe
#initialize graph from file
Grid = nx.read_gml("Bus30Roads.graphml")
Grid = nx.convert_node_labels_to_integers(Grid)
#declare needed constants
SteadyStatePower = 255 #in MW
PlanningHorizon = 12 #this is measured in shifts
ShiftLength = 8 #in Hours

#convert load share to MW
for i in range(0,len(Grid.nodes)):
    if 'load' in Grid.node[i]:
        Grid.node[i]['load'] = Grid.node[i]['load']*SteadyStatePower
#Generate subsets of the multigraph
PowerLines = ((u,v) for u,v,d in Grid.edges(data=True) if d['Type']=='Power')
RoadLines = ((u,v) for u,v,d in Grid.edges(data=True) if d['Type']=='Road')
#import baseloads that were previously calculated
BaseloadMatrixDF = pd.read_csv('BaselineLoads.csv', header=None)
BaseloadMatrix = BaseloadMatrixDF.values.tolist() 
#Declare all iterator sets
Nodes = pe.Set(initialize= range(0,30))
FullNodes = pe.Set(initialize= range(0,37))
Time = pe.Set(initialize = range(0,PlanningHorizon))
Generators = pe.Set(initialize = range(30,37))
#declare model
model = pe.ConcreteModel()
#declare variables for MILP
model.X = pe.Var(FullNodes,FullNodes,Time, domain = pe.Reals)
model.G = pe.Var(Generators,Time, domain = pe.NonNegativeReals)
model.Y = pe.Var(Nodes,Time, domain = pe.Binary)
model.W = pe.Var(FullNodes,FullNodes ,Time, domain = pe.Binary)
model.K = pe.Var(Nodes,Nodes,Time, domain = pe.Binary)
model.F = pe.Var(Nodes,Time, domain = pe.Binary)
model.FE = pe.Var(FullNodes,FullNodes,Time, domain = pe.Binary)
#declare objective
model.obj = pe.Objective(expr = sum(BaseloadMatrix[i][j] - model.X[i,j,t] for t in Time for i in FullNodes for j in FullNodes))
#define flow balance
#line limits
model.con1 = pe.ConstraintList()
for t in Time:
    for a in FullNodes:
        for b in FullNodes:
            if Grid.has_edge(a,b):
                if 'capacity' in Grid[a][b][0]:
                    model.con1.add(model.X[a,b,t]<=Grid[a][b][0]['capacity'])
                    model.con1.add(model.X[a,b,t]>=-1*Grid[a][b][0]['capacity'])
                else:
                    model.con1.add(model.X[a,b,t]==0)
            else:
                model.con1.add(model.X[a,b,t]==0)
#make sure nodes balkance
model.con2 = pe.ConstraintList()
for n in FullNodes:
    for t in Time:
        if 'production' in Grid.node[n]:
            model.con2.add(sum(model.X[k,n,t] for k in FullNodes)+Grid.node[n]['production']==sum(model.X[n,j,t] for j in FullNodes))
        elif 'load' in Grid.node[n]:
            model.con2.add(sum(model.X[k,n,t] for k in FullNodes)==sum(model.X[n,j,t] for j in FullNodes)+Grid.node[n]['load'])
        else:
            model.con2.add(sum(model.X[k,n,t] for k in FullNodes)==sum(model.X[n,j,t] for j in FullNodes))
        for m in FullNodes:
            model.con2.add(model.X[n,m,t]==-1*model.X[m,n,t])
#Define in/out network balance
model.con3 = pe.ConstraintList()
for t in Time:
    model.con3.add(sum(Grid.node[i]['load']*model.Y[i,t] for i in Nodes) == sum(model.G[k,t] for k in Generators))
#define generator capacity balance
model.con4 = pe.ConstraintList()
for t in Time:
    for k in Generators:
        model.con4.add(model.G[k,t] <= Grid.node[k]['production'])
#define maximum flow
model.con5 = pe.ConstraintList()
for t in Time:
    for i in FullNodes:
        for j in FullNodes:
            if Grid.has_edge(i,j,0):
                if 'capacity' in Grid[i][j][0]:
                    model.con5.add(model.X[i,j,t] <= Grid[i][j][0]['capacity'])
            else:
                model.con5.add(model.X[i,j,t]==0)
#scheduling constraint
model.con6 = pe.ConstraintList()
for t in Time:
#assume all nodes take 5 hours to repair and all lines take 1 hour
    model.con6.add(5*sum(model.F[i,t] for i in Nodes) + 1*sum(model.FE[i,j,t] for i in FullNodes for j in FullNodes) <=8)
#generator limits
model.con7 = pe.ConstraintList()
for g in Generators:
    for t in Time:
        model.con4.add(model.G[g,t] <= Grid.node[g]['production'])
        
solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)  
