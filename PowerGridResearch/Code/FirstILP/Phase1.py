# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:30:05 2018

@author: Brian French
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import grinpy as gp
import pandas as pd
import math
import pyomo.environ as pe
from Bus30 import IEEE30

PowerGrid = IEEE30()
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(PowerGrid.nodes(data=True))

#apply newman-watts-strogatz connectivity
NWS_k = 4
NWS_p=.025
DistanceDF = pd.DataFrame(columns = ['From', 'To', 'Distance'])
for i in range(0,30):
    for j in range(0,30):
        SquareX = (RoadGrid.node[i]['xcoord']-RoadGrid.node[j]['xcoord'])**2
        SquareY = (RoadGrid.node[i]['ycoord']-RoadGrid.node[j]['ycoord'])**2
        DistanceDF.loc[j+(i*30)] = [i,j, math.sqrt(SquareX+SquareY)]
#k connections        
for i in range(0,30):
    Subframe = DistanceDF.loc[DistanceDF['From']==i]
    Connect = Subframe.nsmallest(NWS_k,'Distance')
    for index, row in Connect.iterrows():
        RoadGrid.add_edge(i, int(row['To']), length = row['Distance'], IsRoad = True)
#p connections
for i in range(0,30):
    j=i
    while j <= 30:
      rand = np.random.uniform(0,1)  
      if rand <= NWS_p:
          RoadGrid.add_edge(i,j, length=math.sqrt((RoadGrid.node[i]['xcoord']-RoadGrid.node[j]['xcoord'])**2+(RoadGrid.node[i]['ycoord']-RoadGrid.node[j]['ycoord'])**2), IsRoad=True)
      j=j+1
#connecting generators
for i in range(0,len(PowerGrid.nodes)):
    if 'gen' in PowerGrid.node[i]['name']:
        RoadGrid.add_edge(i, list(PowerGrid.neighbors(i))[0], length = 0)

#scenario generation, 4th element is probability
HuricaneLevels = ['cat3','cat4','cat5'] #distribution 50/35/15
Area = ['center','north','west-south'] #distribution 33/33/33
Flooding = ['mild','moderate', 'severe'] #distribution 40/40/20
Size = ['small', 'medium', 'large']  #distribution .25/.5/.25
#ScenarioListing
ScenarioList = []
for i in HuricaneLevels:
    for j in Area:
        for k in Flooding:
            for l in Size:
                ScenarioList.append([i,j,k,l,1])
#remove calculate probabilites for each scenario
for i in range(0,len(ScenarioList)):
    if ScenarioList[i][0]=='cat3':
        ScenarioList[i][4] = ScenarioList[i][4]*.5
    if ScenarioList[i][0]=='cat4':
        ScenarioList[i][4] = ScenarioList[i][4]*.35
    if ScenarioList[i][0]=='cat5':
        ScenarioList[i][4] = ScenarioList[i][4]*.15
    if ScenarioList[i][1]=='north':
        ScenarioList[i][4] = ScenarioList[i][4]*.33
    if ScenarioList[i][1]=='center':
        ScenarioList[i][4] = ScenarioList[i][4]*.34
    if ScenarioList[i][1]=='west-south':
        ScenarioList[i][4] = ScenarioList[i][4]*.33
    if ScenarioList[i][2] == 'mild':
        ScenarioList[i][4] = ScenarioList[i][4]*.4
    if ScenarioList[i][2] == 'moderate':
        ScenarioList[i][4] = ScenarioList[i][4]*.4
    if ScenarioList[i][2] == 'severe':
        ScenarioList[i][4] = ScenarioList[i][4]*.2
    if ScenarioList[i][3] == 'small':
        ScenarioList[i][4] = ScenarioList[i][4]*.25
    if ScenarioList[i][3] == 'medium':
        ScenarioList[i][4] = ScenarioList[i][4]*.5
    if ScenarioList[i][3] == 'large':
        ScenarioList[i][4] = ScenarioList[i][4]*.25
        
        
print(sum(ScenarioList[i][4] for i in range(0,len(ScenarioList))))               

#generate damage list for scenarios
DamageList = []
for i in range(0,len(ScenarioList)):
    if ScenarioList[i][0]=='cat3':
        plinedamage = .4
    if ScenarioList[i][0]=='cat4':
        plinedamage = .5
    if ScenarioList[i][0]=='cat5':
        plinedamage=.75
    if ScenarioList[i][1]=='north':
        lineenter = (22,22)
        lineexit =(0,22)
    if ScenarioList[i][1]=='center':
        lineenter = (22,11)
        lineexit = (0,13)
    if ScenarioList[i][1]=='west-south':
        lineenter = (12,0)
        lineexit = (0,12)
    if ScenarioList[i][2] == 'mild':
        floodpen = 2
    if ScenarioList[i][2] == 'moderate':
        floodpen = 4
    if ScenarioList[i][2] == 'severe':
        floodpen = 6
    if ScenarioList[i][3]=='small':
        damageband = 5
    if ScenarioList[i][3]=='medium':
        damageband = 7
    if ScenarioList[i][3]=='large':
        damageband = 10
    sublist = [plinedamage,lineenter,lineexit,floodpen,damageband]
    DamageList.append(sublist)
#marks potentially damaged edges
B = [ [0] * (len(PowerGrid.nodes())) for _ in range(len(ScenarioList))]
numparts = 2 #spools of wire and transformers (0 and 1 respectively)
Demand = [[0]*numparts for _ in range(len(ScenarioList))]
idx=0
for i in DamageList: 
    #reset everything
    for u in PowerGrid.nodes():
        PowerGrid.node[u]['flooded']=False
        PowerGrid.node[u]['edgeflagged']=False
        
    #handle broken lines
    for u in PowerGrid.nodes():
        for v in PowerGrid.nodes():
            ucoord = PowerGrid.node[u]['pos']
            vcoord = PowerGrid.node[v]['pos']
            udist = abs((i[2][0]-i[1][0])*ucoord[0]+(i[2][1]-i[1][1])*ucoord[1]+i[2][1])/math.sqrt(abs((i[2][0]-i[1][0]))+abs((i[2][1]-i[1][1])))
            vdist = abs((i[2][0]-i[1][0])*vcoord[0]+(i[2][1]-i[1][1])*vcoord[1]+i[2][1])/math.sqrt(abs((i[2][0]-i[1][0]))+abs((i[2][1]-i[1][1])))
            if udist <= i[4]:
                if vdist <= i[4]:
                    if PowerGrid.has_edge(u,v):
                        PowerGrid[u][v]['flagged']=True
                        PowerGrid.node[u]['edgeflagged']=True
                        PowerGrid.node[v]['edgeflagged']=True
    #handle flooded nodes
    for k in PowerGrid.nodes():
        if PowerGrid.node[k]['xcoord'] >= (22-i[3]):
            PowerGrid.node[k]['flooded'] = True
    #compilies broken things down for utilization in a MILP
    for j in range(0,len(PowerGrid.nodes())):
        if PowerGrid.node[j]['edgeflagged']:
            B[idx][j] = B[idx][j]+DamageList[idx][0]
            Demand[idx][0] = Demand[idx][0]+DamageList[idx][0] 
        if PowerGrid.node[j]['flooded']:
            B[idx][j] = B[idx][j]+1
            Demand[idx][1] = Demand[idx][1]+1
    idx = idx+1
#generation of shortest path
D = [[0]*len(PowerGrid.nodes()) for _ in range(len(PowerGrid.nodes))]
for u in RoadGrid.nodes():
    for v in RoadGrid.nodes():
        D[u][v] = nx.shortest_path_length(RoadGrid, source= u, target = v, weight = 'length')
holdingcost = [10,10]
stockoutcost = [25,25]                        
model = pe.ConcreteModel()
Scenarios = pe.Set(initialize = range(0, len(ScenarioList))) 
scenariorange= range(0, int(len(ScenarioList))) #why do I need this hacky workaround
RepairParts = range(0,int(numparts))
Nodes = range(0,int(len(list(PowerGrid.nodes))))
model.L = pe.Var(Nodes, domain = pe.Binary)
model.Q = pe.Var(RepairParts, domain = pe.NonNegativeIntegers)
#used to remove the max function in the model.
model.Qdummy1 = pe.Var(RepairParts, domain = pe.NonNegativeIntegers)
model.Qdummy2 = pe.Var(RepairParts, domain = pe.NonNegativeIntegers)
#model.obj = pe.Objective(expr = sum((ScenarioList[c][4] for c in scenariorange)))
model.obj = pe.Objective(expr = sum((ScenarioList[c][4] *D[i][j]*model.L[i]*B[c][j]) for i in Nodes for j in Nodes for c in scenariorange)+sum((ScenarioList[c][4]*holdingcost[k]*model.Qdummy1[k]) for k in RepairParts for c in scenariorange)+sum((ScenarioList[c][4] *stockoutcost[q]*model.Qdummy2[q]) for q in RepairParts for c in scenariorange),sense=pe.minimize)                      
model.Dummy = pe.ConstraintList()
for p in RepairParts:
    model.Dummy.add(model.Qdummy1[p] >= 0)
    model.Dummy.add(model.Qdummy2[p] >=0)
    for c in range(0, len(ScenarioList)):
        model.Dummy.add(model.Qdummy1[p] >= model.Q[p]-Demand[c][p])
        model.Dummy.add(model.Qdummy2[p] >= Demand[c][p] - model.Q[p])                        
model.Dummy.add(sum(model.L[i] for i in Nodes)==1)
solver = pe.SolverFactory('cplex')
results = solver.solve(model, tee=True)
print(results)                        