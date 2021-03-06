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
    else:
        Grid.node[i]['load'] = 0
#Generate subsets of the multigraph
PowerLines = ((u,v) for u,v,d in Grid.edges(data=True) if d['Type']=='Power')
RoadLines = ((u,v) for u,v,d in Grid.edges(data=True) if d['Type']=='Road')
#import baseloads that were previously calculated
BaseloadMatrixDF = pd.read_csv('BaselineLoads.csv', header=None)
BaseloadMatrix = BaseloadMatrixDF.values.tolist() 
#Declare all iterator sets
FullNodes = pe.Set(initialize= range(0,37))
Time = pe.Set(initialize = range(0,PlanningHorizon))
Generators = pe.Set(initialize = range(30,37))
NormNodes = pe.Set(initialize= range(0,30))
#declare model
model = pe.ConcreteModel()
#declare variables for MILP
model.X = pe.Var(FullNodes,FullNodes,Time, domain = pe.Reals)
model.G = pe.Var(Generators,Time, domain = pe.NonNegativeReals)
model.Y = pe.Var(FullNodes,Time, domain = pe.Binary)
model.W = pe.Var(FullNodes,FullNodes ,Time, domain = pe.Binary)
model.F = pe.Var(NormNodes,Time, domain = pe.Binary)
model.FE = pe.Var(FullNodes,FullNodes,Time, domain = pe.Binary)
model.D = pe.Var(FullNodes,FullNodes,Time, domain = pe.NonNegativeReals)
model.DY = pe.Var(FullNodes, FullNodes,Time, domain = pe.Binary)
#declare objective
model.obj = pe.Objective(expr = sum(model.D[i,j,t] for t in Time for i in FullNodes for j in FullNodes), sense= pe.maximize)
#define functionality
for g in Grid.nodes:
    Grid.node[g]['working']=1
for i in Grid.nodes:
    for j in Grid.nodes:
        if Grid.has_edge(i,j,0):
            if 'capacity' in Grid[i][j][0]:
                Grid[i][j][0]['working']=1
#Do scenario generation
Grid.node[1]['working']=0
Grid.node[5]['working']=0
Grid.node[7]['working']=0
Grid.node[8]['working']=0
Grid.node[17]['working']=0
Grid[1][5][0]['working']=0
Grid[4][6][0]['working']=0
Grid[7][27][0]['working']=0
Grid[14][17][0]['working']=0
Grid[18][19][0]['working']=0
Grid[13][11][0]['working']=0

#introduction of absolute value dummy variables for the objective function  
model.Dummy = pe.ConstraintList()
bigM = 10000
for t in Time:
    for i in FullNodes:
        for j in FullNodes:
            model.Dummy.add(model.D[i,j,t]<=model.X[i,j,t]+bigM*(1-model.DY[i,j,t]))
            model.Dummy.add(model.D[i,j,t]>=(-1*model.X[i,j,t])+(bigM*model.DY[i,j,t]))
#define flow balance
#line limits
model.con1 = pe.ConstraintList()
for t in Time:
    for a in FullNodes:
        for b in FullNodes:
            if Grid.has_edge(a,b):
                if 'capacity' in Grid[a][b][0]:
                    model.con1.add(model.X[a,b,t]<=Grid[a][b][0]['capacity']*model.W[a,b,t])
                    model.con1.add(model.X[a,b,t]>=-1*Grid[a][b][0]['capacity']*model.W[a,b,t])
                    
                    model.con1.add(model.X[a,b,t]<=Grid[a][b][0]['capacity']*model.Y[a,t])
                    model.con1.add(model.X[a,b,t]>=-1*Grid[a][b][0]['capacity']*model.Y[a,t])
                    
                    model.con1.add(model.X[a,b,t]<=Grid[a][b][0]['capacity']*model.Y[b,t])
                    model.con1.add(model.X[a,b,t]>=-1*Grid[a][b][0]['capacity']*model.Y[b,t])
                    model.con1.add(model.X[a,b,t]<=1000*model.W[a,b,t])
                    model.con1.add(model.X[a,b,t]>=-1000*model.W[a,b,t])
                else:
                    model.con1.add(model.X[a,b,t]==0)
            else:
                model.con1.add(model.X[a,b,t]==0)
#make sure nodes balance
model.con2 = pe.ConstraintList()
for n in FullNodes:
    for t in Time:
        if 'production' in Grid.node[n]:
            model.con2.add(sum(model.X[k,n,t] for k in FullNodes)+model.G[n,t]==sum(model.X[n,j,t] for j in FullNodes))
        elif 'load' in Grid.node[n]:
            model.con2.add(sum(model.X[k,n,t] for k in FullNodes)==sum(model.X[n,j,t] for j in FullNodes)+Grid.node[n]['load']*model.Y[n,t])
        else:
            model.con2.add(sum(model.X[k,n,t] for k in FullNodes)==sum(model.X[n,j,t] for j in FullNodes))
#Define in/out network balance
model.con3 = pe.ConstraintList()
for t in Time:
    model.con3.add(sum(Grid.node[i]['load']*model.Y[i,t] for i in NormNodes) == sum(model.G[h,t] for h in Generators))
#define generator capacity balance
model.con4 = pe.ConstraintList()
for t in Time:
    for k in Generators:
        model.con4.add(model.G[k,t] <= Grid.node[k]['production'])
#define maximum flow
#scheduling constraint
model.con6 = pe.ConstraintList()
for t in Time:
#assume all nodes take 5 hours to repair and all lines take 1 hour
    model.con6.add(5*sum(model.F[i,t] for i in NormNodes) + 1*sum(model.FE[i,j,t] for i in FullNodes for j in FullNodes) <=8)
#generator limits
model.con7 = pe.ConstraintList()
for g in Generators:
    for t in Time:
        model.con4.add(model.G[g,t] <= Grid.node[g]['production'])
#handle the repair/is working interaction
model.con8 = pe.ConstraintList()
for t in range(1,len(Time)):
    for n in NormNodes:
      model.con8.add(model.Y[n,t] <= sum(model.F[n,j] for j in range(0,t-1))+Grid.node[n]['working'] )  
    for m in FullNodes:
      for n in FullNodes:
       if Grid.has_edge(n,m,0):
        if 'capacity' in Grid[n][m][0]:
            model.con8.add(model.W[n,m,t] <= sum(model.FE[n,m,j]for j in range(0,t-1))+Grid[m][n][0]['working'])  
solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)  
for a in FullNodes:
    for b in FullNodes:
        for t in Time:
            if model.FE[a,b,t].value != 0:
                print(['a is ', a, 'b is ', b, 't is ',t,])
for n in NormNodes:
    for t in Time:
        if model.F[n,t].value != 0:
            print(['n is ', n, 't is ',t,'value is ',model.F[n,t].value])