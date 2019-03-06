# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:16:26 2019

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
PowerSub = Grid
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = pe.Set(initialize = range(0,len(PowerSub.edges)))
model = pe.ConcreteModel()
#define Variables
##Decision Variables
model.PG = pe.Var(Nodes,Time)
model.F_l = pe.Var(Edges,Time, domain=pe.Binary)
model.F_n = pe.Var(Nodes,Time, domain = pe.Binary)
##State Variables
model.W_l = pe.Var(Edges,Time, domain = pe.Binary)
model.W_n = pe.Var(Nodes, Time, domain = pe.Binary)
model.Theta = pe.Var(Nodes,Time)
model.PowerIJ = pe.Var(Edges,Time, domain = pe.Reals)
for e in PowerSub.edges():
    print(e)
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])

model.obj = pe.Objective(expr = sum((1-model.W_n[i,t])*Grid.node[i]['load'] for i in Nodes for t in Time))

M=1000
model.PAcons = pe.ConstraintList()
for i in Nodes:
    for j in Nodes:
        for t in Time:
         for k in range(0,len(EdgeTracker)):
            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
                    model.PAcons.add(model.PowerIJ[k,t] == model.W_l[k,t]*Grid[i][j][0]['Sus']*(model.Theta[i,t]-model.Theta[j,t]))
        model.PAcons.add(model.Theta[i,t]<=3.14)
        model.PAcons.add(model.Theta[j,t]>=0)
#impose power balance constraints
model.PBcons = pe.ConstraintList()
for i in Nodes:
    for t in Time:
      originadj = []
      destadj = []
      for k in Edges:
          if EdgeTracker[k][1][0] == i:
              originadj.append(k)
          if EdgeTracker[k][1][1]==i:
              destadj.append(k)
      model.PBcons.add(model.PG[i,t]-sum(model.PowerIJ[j,t] for j in originadj)+sum(model.PowerIJ[k,t] for k in destadj) == Grid.node[i]['load']*model.W_n[i,t])
#constrain maximum power generation and handle functionality of the node
for i in Nodes:
    for t in Time:
        model.PBcons.add(model.PG[i,t]<=Grid.node[i]['productionmax']*model.W_n[i,t])
        model.PBcons.add(model.PG[i,t]>=0)
        
model.LineLoadcons = pe.ConstraintList()
for e in Edges:
        for t in Time:
                model.LineLoadcons.add(model.PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_l[e,t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][0],t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][1],t])
                model.LineLoadcons.add(model.PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_l[e,t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][0],t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][1],t])
#model.Working = pe.ConstraintList()
#for i in Nodes:
#    model.Working.add(model.W_n[i,0] == Grid.node[i]['working'])
#    for t in range(1,len(Time)):
#        model.Working.add(model.W_n[i,t]==Grid.node[i]['working'])
#for e in Edges:
#    for t in Time:
#        model.Working.add(model.W_l[e,t]==1)
solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)   
