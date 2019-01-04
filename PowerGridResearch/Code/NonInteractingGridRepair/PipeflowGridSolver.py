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
#determine total load
for n in range(0,30):
        
    TotalLoad += Grid.node[n]['load']   
#declare sets for use in pyomo model
Generators = pe.Set(initialize = range(numgen))

#Declare variables
model.Production = pe.Var(Generators, domain=pe.NonNegativeReals)
model.ProductionAbsoluteDummy = pe.Var(Generators, Generators, domain=pe.NonNegativeReals )

 #optimization criteria is balancing load in generators
model.obj = pe.Objective(expr= sum(sum( model.ProductionAbsoluteDummy[i,j] for j in range(0,i))for i in Generators))

#constratint system 1--handles the dummy production
model.con1 = pe.ConstraintList()
for i in Generators:
    for j in range(0,i):
        model.con1.add(model.ProductionAbsoluteDummy[i,j]>=model.Production[i]-model.Production[j])
        model.con1.add(model.ProductionAbsoluteDummy[i,j]>=model.Production[j]-model.Production[i])
#make sure total load = total production
model.con2 = pe.ConstraintList()
model.con2.add(sum(model.Production[g] for g in Generators)==TotalLoad)
#make sure nodes balkance

#generator limits

#line limits

