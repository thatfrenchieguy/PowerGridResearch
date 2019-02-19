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
Grid = nx.read_gml("Bus30Roads.graphml")
Grid = nx.convert_node_labels_to_integers(Grid)
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 12 #this is measured in shifts
ShiftLength = 8 #in Hours
for n in Grid.nodes:
    if 'load' not in Grid.node[n]:
        Grid.node[n]['load'] = 0
    if 'production' not in Grid.node[n]:
        Grid.node[n]['production']=0
#Define sets to be used in optimiation
Nodes = pe.Set(initialize= range(0,37))
Time = pe.Set(initialize = range(0,PlanningHorizon))
model = pe.ConcreteModel()
#define Variables
##Decision Variables
model.PG = pe.Var(Nodes,Time)
model.F_l = pe.Var(Nodes,Nodes,Time)
model.F_n = pe.Var(Nodes,Time)
##State Variables
model.W_l = pe.Var(Nodes,Nodes,Time)
model.W_n = pe.Var(Nodes, Time)
model.Theta = pe.Var(Nodes,Time)
model.BDummy = pe.Var(Nodes,Nodes,Time)
##Constant Sets
