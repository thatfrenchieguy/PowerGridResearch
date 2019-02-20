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
Grid = nx.read_gml("Bus30WithData.graphml")
Grid = nx.convert_node_labels_to_integers(Grid)
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 12 #this is measured in shifts
ShiftLength = 8 #in Hours
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
model.PowerIJ = pe.Var(Nodes,Nodes,Time)
##Constant Sets
model.obj = pe.Objective(expr = sum((1-model.W_n[i,t])*Grid.node[i]['load'] for i in Nodes for t in Time))

#impose phase angle constraints
model.PAcons = pe.ConstraintList()
    for i in Nodes:
        for j in Nodes:
            for t in Time:
                if 'Sus' in Grid[i][j][0]:
                    model.PAcons.add(model.PowerIJ[i,j,t] = model.BDummy[i,j,t]*(model.Theta[i,t]-model.Theta[j,t]))
#impose power balance constraints
                    