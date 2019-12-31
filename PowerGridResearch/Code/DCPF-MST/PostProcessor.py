# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:58:57 2019

@author: BrianFrench
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from gurobipy import *
#define a powerset function
from itertools import chain, combinations
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#done as node, shift
###import the edge tracker
PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
Nodes = range(0,len(Grid.nodes))
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
          
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
            RoadGrid[i][j]['working']=True
        else:
            RoadGrid.add_edge(i,j,weight = 9999)
            RoadGrid[i][j]['working']=True
###schedule of nodes to be fixed from the pure scheduling solver
InputNodes = [[4,0,'node'],
              [13,1,'node']]
###schedule of edges to be fixed from the pure scheduling solver
InputEdges = [[4,0,'edge'],
              [23,1,'edge']]
RoadData = []
SP = np.zeros((len(Nodes),len(Nodes)))
for i in Nodes:
    for j in Nodes:
        SP[i][j] = nx.shortest_path_length(RoadGrid, source = i, target = j, weight='weight')
        
###packing heuristic
shifts = []
priorityLoadNodes = []
priorityLoadEdges = []
EdgeRepairTime = 1
NodeRepairTime = 5
ShiftLength = 8
shiftBuildNumber = 0
while len(InputNodes)!= 0 and len(InputEdges)!=0:
    cost = 0
    for j in InputNodes:
        if j[1] < shiftBuildNumber and j not in priorityLoadNodes:
            priorityLoadNodes.append(j)
    for i in InputEdges:
        if i[1] < shiftBuildNumber and i not in priorityLoadEdges:
            priorityLoadEdges.append(i)
    lastnode = 13 ###manually change this as needed
    plausibleListNodes = []
    plausibleListEdges = []
    for j in InputNodes:
        if j[1] == shiftBuildNumber:
            plausibleListNodes.append(j[0])
    for i in InputEdges:
        if i[1]==shiftBuildNumber:
            plausibleListEdges.append(i[0])
    ShiftCost = 0
    ShiftUnderConstruction = []
    while ShiftCost<=8:
        NodeCosts = []
        EdgeCosts = []
        for n in plausibleListNodes:
            NodeCost = NodeRepairTime+SP[lastnode][n]
            NodeCosts.append(NodeCost)
        for e in plausibleListEdges:
            EdgeCost1 = EdgeRepairTime+Edgetracker[e][1][0]
            EdgeCost2 = EdgeRepairTime+Edgetracker[e][1][1]
        
    
