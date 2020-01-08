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
PowerSub = nx.read_gml("Bus57WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])
Grid = nx.read_gml("Bus57WithData.gml")
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
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])
###schedule of nodes to be fixed from the pure scheduling solver
InputNodes = [[11,0,'node'],
              [28,1,'node'],
              [14,2,'node'],
              [20,3,'node'],
              [21,4,'node'],
              [4,5,'node'],
              [29,6,'node'],
              [9,7,'node']]
###schedule of edges to be fixed from the pure scheduling solver
InputEdges = [[18,0,'edge'],
              [20,0,'edge'],
              [41,0,'edge'],
              [27,1,'edge'],
              [42,1,'edge'],
              [52,1,'edge'],
              [7,2,'edge'],
              [44,2,'edge'],
              [63,2,'edge'],
              [12,5,'edge'],
              [54,5,'edge'],
              [62,6,'edge']]
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
    print('startingmain')
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
            plausibleListNodes.append(j)
    for i in InputEdges:
        if i[1]==shiftBuildNumber:
            plausibleListEdges.append(i)
    ShiftCost = 0
    ShiftUnderConstruction = []
    while ShiftCost<=8:
        flag = False
        if len(priorityLoadNodes) != 0:
            print('inPriorityNodes')
            NodeCosts = []
            for n in priorityLoadNodes:
                NodeCost = NodeRepairTime+(SP[lastnode][n[0]])/20
                NodeCosts.append(NodeCost)    
            MinNodeCost = min(NodeCosts)
            WhichNode = NodeCosts.index(MinNodeCost)
            CheapestNode = priorityLoadNodes[WhichNode] 
            if MinNodeCost < 8-ShiftCost:
                ShiftUnderConstruction.append([CheapestNode])
                for j in priorityLoadNodes:
                    if j == CheapestNode:
                        priorityLoadNodes = [x for x in priorityLoadNodes if x !=j]
                        InputNodes = [x for x in InputNodes if x !=j]
                flag = True
                lastnode = CheapestNode[0]
                ShiftCost+=MinNodeCost
                
            
        if len(priorityLoadEdges) !=0:
            print('inPriorityEdges')
            EdgeCosts = []
            for e in priorityLoadEdges:
                EdgeCost1 = EdgeRepairTime+SP[lastnode][EdgeTracker[e[0]][1][0]]/20
                EdgeCost2 = EdgeRepairTime+SP[lastnode][EdgeTracker[e[0]][1][1]]/20
                CheaperEdge = min(EdgeCost1, EdgeCost2)
                if CheaperEdge == EdgeCost1:
                    edgenode = EdgeTracker[e[0]][1][0]
                if CheaperEdge == EdgeCost2:
                    edgenode = EdgeTracker[e[0]][1][1]
                EdgeCosts.append([CheaperEdge,edgenode])  
            MinEdgeCost = min(EdgeCosts, key=lambda x: x[0])
            WhichEdge = EdgeCosts.index(MinEdgeCost)
            CheapestEdge = priorityLoadEdges[WhichEdge] 
            if MinEdgeCost[0] < 8-ShiftCost:
                ShiftUnderConstruction.append([CheapestEdge])
                for j in priorityLoadEdges:
                    if j == CheapestEdge:
                        priorityLoadEdges = [x for x in priorityLoadEdges if x !=j]
                        InputEdges = [x for x in InputEdges if x !=j]
                flag = True
                lastnode = MinEdgeCost[1]
                ShiftCost+=MinEdgeCost[0]
        NodeCosts = []
        EdgeCosts = []
        if len(priorityLoadNodes) == 0 and len(priorityLoadEdges)==0:
            print('inPlausibleNodes')
            if len(plausibleListNodes)!=0:
                for n in plausibleListNodes:
                    NodeCost = NodeRepairTime+(SP[lastnode][n[0]])/20
                    NodeCosts.append(NodeCost)    
                MinNodeCost = min(NodeCosts)
                WhichNode = NodeCosts.index(MinNodeCost)
                CheapestNode = plausibleListNodes[WhichNode] 
                if MinNodeCost < 8-ShiftCost:
                    ShiftUnderConstruction.append([CheapestNode])
                    for j in plausibleListNodes:
                        if j == CheapestNode:
                            plausibleListNodes = [x for x in plausibleListNodes if x !=j]
                            InputNodes = [x for x in InputNodes if x !=j]
                    flag = True
                    lastnode = CheapestNode[0]
                    ShiftCost+=MinNodeCost
                
            if len(plausibleListEdges) != 0:
                for e in plausibleListEdges:
                    EdgeCost1 = EdgeRepairTime+SP[lastnode][EdgeTracker[e[0]][1][0]]/20
                    EdgeCost2 = EdgeRepairTime+SP[lastnode][EdgeTracker[e[0]][1][1]]/20
                    CheaperEdge = min(EdgeCost1, EdgeCost2)
                    if CheaperEdge == EdgeCost1:
                        edgenode = EdgeTracker[e[0]][1][0]
                    if CheaperEdge == EdgeCost2:
                        edgenode = EdgeTracker[e[0]][1][1]
                    EdgeCosts.append([CheaperEdge,edgenode])  
                MinEdgeCost = min(EdgeCosts, key=lambda x: x[0])
                WhichEdge = EdgeCosts.index(MinEdgeCost)
                CheapestEdge = plausibleListEdges[WhichEdge] 
                if MinEdgeCost[0] < 8-ShiftCost:
                    ShiftUnderConstruction.append([CheapestEdge])
                    for j in plausibleListEdges:
                        if j == CheapestEdge:
                            plausibleListEdges = [x for x in plausibleListEdges if x !=j]
                            InputEdges = [x for x in InputEdges if x !=j]
                    flag = True
                    lastnode = MinEdgeCost[1]
                
        if flag == False:
            shiftBuildNumber +=1
            shifts.append(ShiftUnderConstruction)
            print(ShiftUnderConstruction)
            ShiftUnderConstruction = []
            ShiftCost = 0
            print('bang')
            break
            
