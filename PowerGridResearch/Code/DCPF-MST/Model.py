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
#define a powerset function
from itertools import chain, combinations
def powerset(iterable):
    "list(powerset([1,2,3])) --> [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#initialize graph from file
Grid = nx.read_gml("Bus30WithData.gml")
Grid = nx.convert_node_labels_to_integers(Grid)
#declare needed constants
SteadyStatePower = 255 #in MW--the PU Basis
PlanningHorizon = 12 #this is measured in shifts
ShiftLength = 8 #in Hours
#Define sets to be used in optimiation
PowerSub = nx.read_gml("Bus30WithData.gml")
PowerSub = nx.convert_node_labels_to_integers(PowerSub)
for i in PowerSub.nodes:
  for j in PowerSub.nodes:
    if PowerSub.has_edge(i,j,1):
        PowerSub.remove_edge(i,j,1)
Edges = pe.Set(initialize = range(0,len(PowerSub.edges)))
Nodes = pe.Set(initialize= range(0,30))
sumlen = 71
#sumlen = len(Nodes)+len(Edges)
NodesWithDummy = pe.Set(initialize = range(0,sumlen))
Time = pe.Set(initialize = range(0,PlanningHorizon))
model = pe.ConcreteModel()
#define Variables
#Decision Variables
model.PG = pe.Var(Nodes,Time)
model.F_l = pe.Var(Edges,Time, domain=pe.Binary)
model.F_n = pe.Var(Nodes,Time, domain = pe.Binary)
model.Z = pe.Var(NodesWithDummy,NodesWithDummy,Time, domain = pe.Binary) #abuse total unimodularity to speed up the solving time if needed
##State Variables
model.W_l = pe.Var(Edges,Time, domain = pe.Binary)
model.W_n = pe.Var(Nodes, Time, domain = pe.Binary)
model.Theta = pe.Var(Nodes,Time)
model.PowerIJ = pe.Var(Edges,Time, domain = pe.Reals)
model.MST = pe.Var(Time, domain = pe.NonNegativeReals)
#default everything to working
for i in Nodes:
    nx.set_node_attributes(Grid, {i:True},'working')
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            Grid[i][j][0]['working']=True
##artblock
x  = nx.get_node_attributes(Grid,('xcoord'))
y = nx.get_node_attributes(Grid,'ycoord')
pos=[]
power = []
road = []
for i in x:
    pos.append((x[i],y[i]))
for e in Grid.edges:
    if e[2]==0:
        power.append(e)
    if e[2]==1:
        road.append(e)
        
nx.draw_networkx_nodes(Grid, pos, label=True)
nx.draw_networkx_labels(Grid, pos)
nx.draw_networkx_edges(Grid, pos, edgelist = power, edge_color = "g", width = 2, alpha =.7)
nx.draw_networkx_edges(Grid, pos, edgelist = road, edge_color = 'r', width = 2, alpha = .7)
#
plt.axis('off')
plt.show()
#######            
###SCENARIO OF BROKEN THINGS###
Grid.node[6]['working']=False
Grid.node[27]['working']=False
Grid.node[23]['working']=False
Grid.node[18]['working']=False
Grid.node[15]['working']=False
Grid[1][4][0]['working']=False
Grid[4][6][0]['working']=False
Grid[7][27][0]['working']=False
Grid[24][25][0]['working']=False
Grid[11][15][0]['working']=False
Grid[1][3][0]['working']=False
Grid[19][18][0]['working']=False
###END SCENARIO###            
EdgeTracker = [] #this is an index i connected to a tuple where element 1 is the origin and element 2 is the destination
for i,e in enumerate(PowerSub.edges):
    EdgeTracker.append([i,e])
#status tracker for edges since they've been seperated from the grid datastructure
EdgeStartingStatus = np.zeros(len(EdgeTracker))
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,0):
            for k in range(0,len(EdgeTracker)):
                if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
                    EdgeStartingStatus[k] = Grid[i][j][0]['working']
model.obj = pe.Objective(expr = sum((1-model.W_n[i,t])*Grid.node[i]['load'] for i in Nodes for t in Time))


#impose phase angle constraints

M=1000
model.PAcons = pe.ConstraintList()
for i in Nodes:
    for j in Nodes:
        for t in Time:
         for k in range(0,len(EdgeTracker)):
            if EdgeTracker[k][1][0] == i and EdgeTracker[k][1][1]==j:
                    model.PAcons.add(model.PowerIJ[k,t] == Grid[i][j][0]['Sus']*(model.Theta[i,t]-model.Theta[j,t]))
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
#constrain line limits
model.LineLoadcons = pe.ConstraintList()
for e in Edges:
        for t in Time:
                model.LineLoadcons.add(model.PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_l[e,t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][0],t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]<=Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][1],t])
                model.LineLoadcons.add(model.PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_l[e,t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][0],t])     
                model.LineLoadcons.add(model.PowerIJ[e,t]>=-1*Grid[EdgeTracker[e][1][0]][EdgeTracker[e][1][1]][0]['capacity']*model.W_n[EdgeTracker[e][1][1],t])                
           

#define workingness
model.Working = pe.ConstraintList()
for i in Nodes:
    model.Working.add(model.W_n[i,0] <= Grid.node[i]['working'])
    for t in range(1,len(Time)):
        model.Working.add(model.W_n[i,t]<=sum(model.F_n[i,g] for g in range(0,t))+Grid.node[i]['working'])
for e in Edges:
    for t in Time:
        model.Working.add(model.W_l[e,t]<=sum(model.F_l[e,g] for g in range(0,t))+EdgeStartingStatus[e])
        
##schedule restriction so that nothing gets double fixed
#for i in Nodes:
#    model.Working.add(sum(model.F_n[i,t]for t in Time)<=1)   
#for e in Edges:
#    model.Working.add(sum(model.F_l[e,t]for t in Time)<=1)         
#build shortest path matrix
SP = np.zeros((len(NodesWithDummy), len(NodesWithDummy)))
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
for i,e in enumerate(EdgeTracker):
    RoadGrid.add_node(30+i)
    RoadGrid.add_edge(30+i, e[1][0], weight = 0)
    RoadGrid.add_edge(30+i, e[1][1], weight=0)
for i in NodesWithDummy:
    for j in NodesWithDummy:
        SP[i][j] = nx.shortest_path_length(RoadGrid, source = i, target = j, weight='weight')
model.MSTCons = pe.ConstraintList()
for t in Time:
    model.MSTCons.add(model.MST[t] == sum(SP[i][j]*model.Z[i,j,t] for i in NodesWithDummy for j in NodesWithDummy))
    model.MSTCons.add(sum(model.Z[i,j,t] for i in NodesWithDummy for j in NodesWithDummy) == sum(model.F_n[i,t]for i in Nodes)+sum(model.F_l[e,t] for e in Edges)-1)
    for s in powerset(NodesWithDummy):
        if len(s)>=2 and len(s) <=8:
            model.MSTCons.add(sum(model.Z[i,j,t] for i in s for j in s)<=len(s)-1)
    for i in Nodes:
#        dropi = Nodes
#        dropi.remove(i)
       model.MSTCons.add(sum(model.Z[i,j,t] for j in Nodes)>=model.F_n[i,t])
    for e in Edges:
        i = EdgeTracker[e][1][0]
        j = EdgeTracker[e][1][1]
        E = len(Nodes)+e
        model.MSTCons.add(sum(model.Z[E,j,t] for j in NodesWithDummy) <= model.F_l[e,t])
#arbitrarily assigning node 13 to be the warehouse node
model.Scheduling = pe.ConstraintList()
for t in Time:
    model.Scheduling.add(sum(model.F_n[i,t]*5 for i in Nodes)+sum(model.F_l[e,t]*1 for e in Edges)+model.MST[t]<=8)

solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)    
for t in Time:
    for i in Nodes:
        if model.W_n[i,t].value <1:
            print(["Wtime",t,"node",i])
for t in Time:
    for e in Edges:
        if model.W_l[e,t].value <1:
            print(["Wtime",t,"edge",e])
for t in Time:
    for i in Nodes:
        if model.F_n[i,t].value==1:
            print(['Ftime',t,"node",i])
    for e in Edges:
        if model.F_l[e,t].value==1:
            print(['Ftime',t,"edge",e])
    