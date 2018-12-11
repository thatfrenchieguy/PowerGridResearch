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
    Grid.node[i]['load'] = Grid.node[i]['load']*SteadyStatePower
#Generate subsets of the multigraph
PowerLines = ((u,v) for u,v,d in Grid.edges(data=True) if d['Type']=='Power')
RoadLines = ((u,v) for u,v,d in Grid.edges(data=True) if d['Type']=='Road')
#Declare all iterator sets
Nodes = pe.Set(initialize= range(0,30))
FullNodes = pe.Set(initialize= range(0,30))
Time = pe.Set(initialize = range(0,PlanningHorizon))
Generators = pe.set(initialize = range(30,37))
#declare model
model = pe.ConcreteModel()
#declare variables for MILP
model.Z = pe.Var(Nodes,Time, domain= pe.NonNegativeReals)
model.X = pe.Var(FullNodes,FullNodes,Time, domain = pe.Reals)
model.G = pe.Var(Generators,Time, domain = pe.NonNegativeReals)
model.Y = pe.Var(Nodes,Time, domain = pe.Binary)
model.W = pe.Var(PowerLinesSet,Time, domain = pe.Binary)
model.S = pe.Var(Nodes,Time, domain = pe.Binary)
model.K = pe.Var(Nodes,Nodes,Time, domain = pe.Binary)
model.F = pe.Var(Nodes,Time, domain = pe.Binary)
#declare objective
model.obj = pe.Objective(expr = sum(SteadyStateFlow[i] - model.Z[i,t] for t in Time for i in Nodes))
#Define total Flow
model.con1 = pe.ConstraintList()
for t in Time:
    for i in Nodes:
        model.con1.add(model.Z[i,t] == model.Y[i]*sum(model.X[j,i,t] for j in FullNodes))
#define flow balance
model.con2 = pe.ConstraintList()
for t in Time:
    for k in Nodes:
        model.con2(sum(model.X[i,k] for i in FullNodes)==sum(model.X[k,j] for j in FullNodes)-Grid.node[k]['load'])
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
                model.con5.add(model.X[i,j,t] <= Grid.edges[i,j,0]['capacity'])
            else:
                model.con5.add(model.X[i,j,t]==0)
#scheduling constraint
model.con6 = pe.ConstraintList()
for t in Time: