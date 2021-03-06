# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 20:12:39 2019

@author: Brian French
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import pyomo.environ as pe
import os
import csv
os.path.dirname(os.path.abspath(__file__))
#initialize graph from file
Grid = nx.read_gml("Bus30Roads.graphml")
Grid = nx.convert_node_labels_to_integers(Grid)
SteadyStateLoad = 255 #load measured in megawatts
#convert load share to MW
for i in range(0,30):
    
    Grid.node[i]['load'] = round(Grid.node[i]['load']*SteadyStateLoad,3)
    
#declare model
model = pe.ConcreteModel()
#declare sets used as iterables
##count generators 
numgen = 0
TotalLoad = 0
for n in range(0,len(Grid.nodes)):
    if 'gen' in Grid.node[n]['name']:
        numgen +=1
NumNonGenNodes = len(Grid)-numgen    
#determine total load
for n in range(0,NumNonGenNodes):
        
    TotalLoad += Grid.node[n]['load']   
#declare sets for use in pyomo model
Generators = pe.Set(initialize = range(numgen))
Nodes = pe.Set(initialize = range(len(Grid)))
#Declare variables
model.Production = pe.Var(Generators, domain=pe.NonNegativeReals)
model.ProductionAbsoluteDummy = pe.Var(Generators, Generators, domain=pe.NonNegativeReals )
model.LineFlow = pe.Var(Nodes,Nodes, domain = pe.Reals)
 #optimization criteria is balancing load in generators
model.obj = pe.Objective(expr= sum(sum( model.ProductionAbsoluteDummy[i,j] for j in range(0,i))for i in Generators))

#constratint system 1--handles the dummy production
model.con1 = pe.ConstraintList()
for i in Generators:
    for j in range(0,i):
        model.con1.add(model.ProductionAbsoluteDummy[i,j]>=model.Production[i]/Grid.node[30+i]['production']-model.Production[j]/Grid.node[30+j]['production'])
        model.con1.add(model.ProductionAbsoluteDummy[i,j]>=model.Production[j]/Grid.node[30+j]['production']-model.Production[i]/Grid.node[30+i]['production'])
#make sure total load = total production
model.con2 = pe.ConstraintList()
model.con2.add(sum(model.Production[g] for g in Generators)==TotalLoad)
#make sure nodes balkance
model.con3 = pe.ConstraintList()
for n in Nodes:
    if 'production' in Grid.node[n]:
        model.con3.add(sum(model.LineFlow[k,n] for k in Nodes)+model.Production[n-30]==sum(model.LineFlow[n,j] for j in Nodes))
    elif 'load' in Grid.node[n]:
        model.con3.add(sum(model.LineFlow[k,n] for k in Nodes)==sum(model.LineFlow[n,j] for j in Nodes)+Grid.node[n]['load'])
    else:
        model.con3.add(sum(model.LineFlow[k,n] for k in Nodes)==sum(model.LineFlow[n,j] for j in Nodes))
for g in Generators:
    model.con3.add(sum(model.LineFlow[30+g,k] for k in Nodes) == model.Production[g])
#generator limits
model.con4 = pe.ConstraintList()
for g in Generators:
    model.con4.add(model.Production[g] <= Grid.node[30+g]['production'])
#line limits
model.con5 = pe.ConstraintList()
for a in Nodes:
    for b in Nodes:
        if Grid.has_edge(a,b):
            if 'capacity' in Grid[a][b][0]:
                model.con5.add(model.LineFlow[a,b]<=Grid[a][b][0]['capacity'])
                model.con5.add(model.LineFlow[a,b]>=-1*Grid[a][b][0]['capacity'])
            else:
                model.con5.add(model.LineFlow[a,b]==0)
        else:
                model.con5.add(model.LineFlow[a,b]==0)
solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)               
#outputs
for g in Generators:
    print(model.Production[g].value)

outputMatrix = [[0 for col in range(len(Nodes))] for row in range(len(Nodes))]
for a in Nodes:
    for b in Nodes:
        if model.LineFlow[a,b].value != 0:
          #  print(model.LineFlow[a,b].value)                
            outputMatrix[a][b] = model.LineFlow[a,b].value
            
csvfile = "BaselineLoads.csv"            
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(outputMatrix)
#statement used in debugging check
#for a in Nodes:
#    for b in Nodes:
#        if Grid.has_edge(a,b):
#          if 'capacity' in Grid[a][b][0]:
#              print("a is:"+str(a))
#              print("b is:"+str(b))
#              print(Grid[a][b][0]['capacity'])
