# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 12:41:58 2019

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
Nodes = range(0,30)
Time = range(0,PlanningHorizon)
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
        else:
            RoadGrid.add_edge(i,j,weight = 9999)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            if np.random.uniform(0,10)<=2:
                RoadGrid[i][j]['working']=False
            else:
                RoadGrid[i][j]['working']=True
        else:
            RoadGrid[i][j]['working']=True
#define Variables
model = pe.ConcreteModel()
C=np.zeros((30,30))
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            C[i][j]=3
model.X = pe.Var(Nodes, Nodes, Time, domain = pe.Binary)
model.S = pe.Var(Nodes, Nodes, Time, domain = pe.NonNegativeReals)
model.K = pe.Var(Nodes, Nodes, Time, domain = pe.Binary)
model.obj = pe.Objective(expr = sum(1.02*t*C[i][j]*(1-model.X[i,j,t]) for i in Nodes for j in Nodes for t in Time), sense=pe.minimize)
model.Con1 = pe.ConstraintList()
for t in Time:
     model.Con1.add(sum(model.S[i,j,t]*model.K[i,j,t] for i in Nodes for j in Nodes)<=8)
model.Con2 = pe.ConstraintList()
for i in Nodes:
    for j in Nodes:
        for t in Time:
            model.Con2.add(model.S[i,j,t] >= RoadGrid[i][j]['weight'])
            model.Con2.add(model.S[i,j,t] >= (1-model.X[i,j,t])*RoadGrid[i][j]['weight']*4) #R_ij is set to 4 length
#tour connectivity constraints           
model.Con3 = pe.ConstraintList()
for i in Nodes:
    for t in Time:
        model.Con3.add(sum(model.K[i,j,t] for j in Nodes)-sum(model.K[j,i,t] for j in Nodes)==0)
def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]]+item
            yield item
S = powerset(list(range(30)))
#depot is at 14
for t in Time:
    model.Con3.add(sum( model.K[14,i,t] for i in Nodes) == 1)
    model.Con3.add(sum( model.K[i,14,t] for i in Nodes) == 1)

#functionality constraints
model.Con4 = pe.ConstraintList()
for i in Nodes:
    for j in Nodes:
        model.Con4.add(model.X[i,j,t] == int(RoadGrid[i][j]['working']))
        for t in range(1,PlanningHorizon):
            model.X[i,j,t] <= sum(model.K[i,j,v] for v in range(0,t))+int(RoadGrid[i][j]['working'])
#DFJ subtour eliminations
model.Con5 = pe.ConstraintList()
for s in S:
    for t in Time:
        if len(s) >=2:
            if len(s)<=28:
                model.Con5.add(sum(model.K[i,j,t] for i in Nodes for j in Nodes)<= len(s)-1)
                
solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)   
