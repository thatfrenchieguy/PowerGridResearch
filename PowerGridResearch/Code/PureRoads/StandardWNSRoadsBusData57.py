# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:16:46 2018

@author: BrianFrench
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 10:08:13 2018

@author: Brian French
"""

#hardcoding bus30--loads taken from http://motor.ece.iit.edu/Data/tgplan30.doc
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import pyomo.environ as pe

Grid = nx.MultiGraph()
#apply coordinates from http://pubs.sciepub.com/ajeee/4/3/4/figure/5 with a best guess taken from looking at it and overlaying a grid
Grid.add_node(0,name = "bus1", load = 55, productionmax = 200, xcoord = 27, ycoord=30)
Grid.add_node(1,name = "bus2", load = 3,productionmax = 0, xcoord = 20, ycoord = 30)
Grid.add_node(2,name = "bus3", load = 41,productionmax = 100, xcoord=17, ycoord=30)
Grid.add_node(3,name = "bus4", load = 0,productionmax = 0, xcoord =6,ycoord=30)
Grid.add_node(4,name = "bus5", load = 13,productionmax = 0, xcoord=2, ycoord=30)
Grid.add_node(5,name = "bus6", load = 75,productionmax = 0, xcoord=2, ycoord=26)
Grid.add_node(6,name = "bus7", load =0,productionmax = 0, xcoord = 2, ycoord=7)
Grid.add_node(7,name = "bus8", load =150,productionmax = 450, xcoord=5,ycoord=2)
Grid.add_node(8,name = "bus9", load = 121,productionmax = 0, xcoord=25, ycoord=2)
Grid.add_node(9,name = "bus10", load = 5,productionmax = 0, xcoord=28, ycoord=8)
Grid.add_node(10,name = "bus11", load = 0,productionmax = 00, xcoord=25, ycoord=9)
Grid.add_node(11,name = "bus12", load = 377,productionmax = 400, xcoord=30, ycoord=22)
Grid.add_node(12,name = "bus13", load = 18,productionmax = 00, xcoord=26, ycoord=22)
Grid.add_node(13,name = "bus14", load = 10.5,productionmax = 0, xcoord=16, ycoord=22)
Grid.add_node(14,name = "bus15", load = 22,productionmax = 0, xcoord=16, ycoord=26)
Grid.add_node(15,name = "bus16", load = 43,productionmax = 0, xcoord=30, ycoord=30)
Grid.add_node(16,name = "bus17", load = 42, productionmax = 0, xcoord=28, ycoord=28)
Grid.add_node(17,name = "bus18", load = 27.2,productionmax = 0, xcoord=5, ycoord=27)
Grid.add_node(18,name = "bus19", load= 3.3,productionmax = 0, xcoord=8, ycoord=27)
Grid.add_node(19,name = "bus20", load = 2.3,productionmax = 0, xcoord=11, ycoord=27)
Grid.add_node(20,name = "bus21", load = 0,productionmax = 0, xcoord=11, ycoord=23)
Grid.add_node(21,name = "bus22", load = 0,productionmax = 0, xcoord=11, ycoord=13)
Grid.add_node(22,name = "bus23", load = 6.3,productionmax = 0, xcoord=10, ycoord=13)
Grid.add_node(23,name = "bus24", load = 0,productionmax = 0, xcoord=8, ycoord=13)
Grid.add_node(24,name = "bus25", load = 6.3,productionmax = 0, xcoord=8, ycoord=10)
Grid.add_node(25,name = "bus26", load = 0,productionmax = 0, xcoord=6, ycoord=12)
Grid.add_node(26,name = "bus27", load = 9.3,productionmax = 0, xcoord=6, ycoord=8)
Grid.add_node(27,name = "bus28", load = 4.6,productionmax = 0, xcoord=6, ycoord=6)
Grid.add_node(28,name = "bus29", load = 17,productionmax = 0, xcoord=5, ycoord=2 )
Grid.add_node(29,name = "bus30", load = 3.6,productionmax = 0, xcoord=7, ycoord=12)
Grid.add_node(30,name = "bus31", load = 5.8,productionmax = 0, xcoord=9, ycoord=6)
Grid.add_node(31,name = "bus32", load = 1.6,productionmax = 0, xcoord=11, ycoord=6)
Grid.add_node(32,name = "bus33", load = 3.8,productionmax = 0, xcoord=11, ycoord=9)
Grid.add_node(33,name = "bus34", load = 0,productionmax = 0, xcoord=15, ycoord=7)
Grid.add_node(34,name = "bus35", load = 6,productionmax = 0, xcoord=15, ycoord=9)
Grid.add_node(35,name = "bus36", load = 0,productionmax = 300, xcoord=16, ycoord=10)
Grid.add_node(36,name = "bus37", load = 0,productionmax = 0, xcoord=15, ycoord=13)
Grid.add_node(37,name = "bus38", load = 14,productionmax = 0, xcoord=15, ycoord=15)
Grid.add_node(38,name = "bus39", load = 0,productionmax = 0, xcoord=17, ycoord=16)
Grid.add_node(39,name = "bus40", load = 0,productionmax = 0, xcoord=17, ycoord=10)
Grid.add_node(40,name = "bus41", load = 6.3,productionmax = 0, xcoord=22, ycoord=11)
Grid.add_node(41,name = "bus42", load = 7.1,productionmax = 0, xcoord=19, ycoord=8)
Grid.add_node(42,name = "bus43", load = 2,productionmax = 0, xcoord=21, ycoord=7)
Grid.add_node(43,name = "bus44", load = 12,productionmax = 0, xcoord=13, ycoord=19)
Grid.add_node(44,name = "bus45", load = 0,productionmax = 0, xcoord=12, ycoord=27)
Grid.add_node(45,name = "bus46", load = 0,productionmax = 0, xcoord=16, ycoord=20)
Grid.add_node(46,name = "bus47", load = 29.7,productionmax = 0, xcoord=16, ycoord=17)
Grid.add_node(47,name = "bus48", load = 0,productionmax = 0, xcoord=16, ycoord=14)
Grid.add_node(48,name = "bus49", load = 18,productionmax = 0, xcoord=19, ycoord=14)
Grid.add_node(49,name = "bus50", load = 21,productionmax = 0, xcoord=30, ycoord=15)
Grid.add_node(50,name = "bus51", load = 18,productionmax = 0, xcoord=30, ycoord=2)
Grid.add_node(51,name = "bus52", load = 4.9,productionmax = 0, xcoord=7, ycoord=5)
Grid.add_node(52,name = "bus53", load = 20,productionmax = 0, xcoord=10, ycoord=5)
Grid.add_node(53,name = "bus54", load = 4.1,productionmax = 0, xcoord=16, ycoord=6)
Grid.add_node(54,name = "bus55", load = 6.8,productionmax = 0, xcoord=20, ycoord=5)
Grid.add_node(55,name = "bus56", load = 7.6,productionmax = 0, xcoord=19, ycoord=10)
Grid.add_node(56,name = "bus57", load = 6.7,productionmax = 0, xcoord=19, ycoord=16)
#turn coords into position to make plotable
#bus 57 edges
Grid.add_edge(0,1, key=0, capacity = int(200), Type = "Power", Sus = float(35.71))
Grid.add_edge(1,2, key=0, capacity = int(100), Type = "Power", Sus = float(11.76))
Grid.add_edge(2,3, key=0, capacity = int(150), Type = "Power", Sus = float(27.32))
Grid.add_edge(3,4, key=0, capacity = int(75), Type = "Power", Sus = float(7.57))
Grid.add_edge(3,5, key=0, capacity = int(75), Type = "Power", Sus = float(6.76))
Grid.add_edge(5,6, key=0, capacity = int(75), Type = "Power", Sus = float(9.8))
Grid.add_edge(5,7, key=0, capacity = int(75), Type = "Power", Sus = float(5.78))
Grid.add_edge(7,8, key=0, capacity = int(100), Type = "Power", Sus = float(19.80))
Grid.add_edge(8,9, key=0, capacity = int(75), Type = "Power", Sus = float(5.96))
Grid.add_edge(8,10, key=0, capacity = int(100), Type = "Power", Sus = float(11.79))
Grid.add_edge(8,11, key=0, capacity = int(50), Type = "Power", Sus = float(3.39))
Grid.add_edge(8,12, key=0, capacity = int(75), Type = "Power", Sus = float(6.33))  
Grid.add_edge(12,13, key=0, capacity = int(150), Type = "Power", Sus = float(23.041))
Grid.add_edge(12,14, key=0, capacity = int(100), Type = "Power", Sus = float(11.507))
Grid.add_edge(0,14, key=0, capacity = int(100), Type = "Power", Sus = float(10.989))
Grid.add_edge(0,15, key=0, capacity = int(75), Type = "Power", Sus = float(4.854))
Grid.add_edge(0,16, key=0, capacity = int(75), Type = "Power", Sus = float(9.259))
Grid.add_edge(2,14, key=0, capacity = int(25), Type = "Power", Sus = float(18.867))
Grid.add_edge(3,17, key=0, capacity = int(50), Type = "Power", Sus = float(1.801))
Grid.add_edge(4,5, key=0, capacity = int(100), Type = "Power", Sus = float(15.600))
Grid.add_edge(6,7, key=0, capacity = int(100), Type = "Power", Sus = float(14.044))
Grid.add_edge(9,11, key=0, capacity = int(100), Type = "Power", Sus = float(7.923))
Grid.add_edge(10,12, key=0, capacity = int(100), Type = "Power", Sus = float(13.66))
Grid.add_edge(11,12, key=0, capacity = int(100), Type = "Power", Sus = float(17.241))
Grid.add_edge(11,15, key=0, capacity = int(100), Type = "Power", Sus = float(12.300))
Grid.add_edge(11,16, key=0, capacity = int(100), Type = "Power", Sus = float(5.586))
Grid.add_edge(13,14, key=0, capacity = int(100), Type = "Power", Sus = float(18.281))
Grid.add_edge(17,18, key=0, capacity = int(50), Type = "Power", Sus = float(1.459))
Grid.add_edge(18,19, key=0, capacity = int(50), Type = "Power", Sus = float(2.304))
Grid.add_edge(19,20, key=0, capacity = int(50), Type = "Power", Sus = float(1.287))
Grid.add_edge(20,21, key=0, capacity = int(50), Type = "Power", Sus = float(8.547))
Grid.add_edge(21,22, key=0, capacity = int(500), Type = "Power", Sus = float(65.789))
Grid.add_edge(22,23, key=0, capacity = int(50), Type = "Power", Sus = float(3.906))
Grid.add_edge(23,24, key=0, capacity = int(25), Type = "Power", Sus = float(.846))
Grid.add_edge(23,25, key=0, capacity = int(200), Type = "Power", Sus = float(21.141))
Grid.add_edge(25,26, key=0, capacity = int(50), Type = "Power", Sus = float(3.937))
Grid.add_edge(26,27, key=0, capacity = int(100), Type = "Power", Sus = float(10.482))
Grid.add_edge(27,28, key=0, capacity = int(100), Type = "Power", Sus = float(17.035))
Grid.add_edge(6,28, key=0, capacity = int(100), Type = "Power", Sus = float(15.432))
Grid.add_edge(24,29, key=0, capacity = int(50), Type = "Power", Sus = float(4.95))
Grid.add_edge(29,30, key=0, capacity = int(50), Type = "Power", Sus = float(2.01))
Grid.add_edge(30,31, key=0, capacity = int(25), Type = "Power", Sus = float(1.324))
Grid.add_edge(31,32, key=0, capacity = int(200), Type = "Power", Sus = float(27.777))
Grid.add_edge(31,33, key=0, capacity = int(25), Type = "Power", Sus = float(1.049))
Grid.add_edge(33,34, key=0, capacity = int(100), Type = "Power", Sus = float(12.82))
Grid.add_edge(34,35, key=0, capacity = int(100), Type = "Power", Sus = float(18.621))
Grid.add_edge(35,36, key=0, capacity = int(200), Type = "Power", Sus = float(27.322))
Grid.add_edge(36,37, key=0, capacity = int(100), Type = "Power", Sus = float(9.910))
Grid.add_edge(36,38, key=0, capacity = int(200), Type = "Power", Sus = float(26.385))
Grid.add_edge(35,39, key=0, capacity = int(200), Type = "Power", Sus = float(21.459))
Grid.add_edge(21,37, key=0, capacity = int(300), Type = "Power", Sus = float(33.898))
Grid.add_edge(10,40, key=0, capacity = int(25), Type = "Power", Sus = float(1.3351))
Grid.add_edge(40,41, key=0, capacity = int(50), Type = "Power", Sus = float(2.841))
Grid.add_edge(40,42, key=0, capacity = int(50), Type = "Power", Sus = float(2.427))
Grid.add_edge(37,43, key=0, capacity = int(150), Type = "Power", Sus = float(17.09))
Grid.add_edge(14,44, key=0, capacity = int(100), Type = "Power", Sus = float(9.596))
Grid.add_edge(13,45, key=0, capacity = int(100), Type = "Power", Sus = float(13.605))
Grid.add_edge(45,46, key=0, capacity = int(100), Type = "Power", Sus = float(14.705))
Grid.add_edge(46,47, key=0, capacity = int(500), Type = "Power", Sus = float(42.918))
Grid.add_edge(47,48, key=0, capacity = int(50), Type = "Power", Sus = float(7.752))
Grid.add_edge(48,49, key=0, capacity = int(50), Type = "Power", Sus = float(7.813))
Grid.add_edge(49,50, key=0, capacity = int(50), Type = "Power", Sus = float(4.54))
Grid.add_edge(9,50, key=0, capacity = int(100), Type = "Power", Sus = float(14.044))
Grid.add_edge(12,48, key=0, capacity = int(75), Type = "Power", Sus = float(5.236))
Grid.add_edge(28,51, key=0, capacity = int(75), Type = "Power", Sus = float(5.347))
Grid.add_edge(51,52, key=0, capacity = int(100), Type = "Power", Sus = float(10.16))
Grid.add_edge(52,53, key=0, capacity = int(75), Type = "Power", Sus = float(4.31))
Grid.add_edge(53,54, key=0, capacity = int(75), Type = "Power", Sus = float(4.424))
Grid.add_edge(10,42, key=0, capacity = int(75), Type = "Power", Sus = float(6.536))
Grid.add_edge(43,44, key=0, capacity = int(75), Type = "Power", Sus = float(8.064))
Grid.add_edge(39,55, key=0, capacity = int(25), Type = "Power", Sus = float(.836))
Grid.add_edge(40,55, key=0, capacity = int(50), Type = "Power", Sus = float(1.821))
Grid.add_edge(41,55, key=0, capacity = int(50), Type = "Power", Sus = float(2.824))
Grid.add_edge(38,56, key=0, capacity = int(50), Type = "Power", Sus = float(1.355))
Grid.add_edge(55,56, key=0, capacity = int(50), Type = "Power", Sus = float(3.84))
Grid.add_edge(37,48, key=0, capacity = int(75), Type = "Power", Sus = float(5.649))
Grid.add_edge(37,47, key=0, capacity = int(200), Type = "Power", Sus = float(20.746))
Grid.add_edge(8,54, key=0, capacity = int(75), Type = "Power", Sus = float(8.298))


#colouring nodes correctly--green is loaded node, red is buss, blue is generator
    #todo when I figure out why it's completely fucked trying to access datavalues

#code below was run once to generate a standard road network, then saved to file and commented out
#apply newman-watts-strogatz connectivity
NWS_k = 3
NWS_p=.03
DistanceDF = pd.DataFrame(columns = ['From', 'To', 'Distance'])
for i in range(0,57):
    for j in range(0,57):
        SquareX = (Grid.node[i]['xcoord']-Grid.node[j]['xcoord'])**2
        SquareY = (Grid.node[i]['ycoord']-Grid.node[j]['ycoord'])**2
        DistanceDF.loc[j+(i*57)] = [i,j, math.sqrt(SquareX+SquareY)]
#k connections        
for i in range(0,57):
    Subframe = DistanceDF.loc[DistanceDF['From']==i]
    Subframe = Subframe[Subframe.To != i]
    Subframe = Subframe[Subframe.To <=56]
    Connect = Subframe.nsmallest(NWS_k,'Distance')
    for index, row in Connect.iterrows():
        if (int(row['To']) != i) and (Grid.has_edge(i, int(row['To']))==False):
            Grid.add_edge(i, int(row['To']), key=1, length = float(row['Distance']), Type = "Road")
#p connections
for i in range(0,57):
    j=i
    while j < 57:
        rand = np.random.uniform(0,1)  
        if (rand <= NWS_p) and (i!=j) and (Grid.has_edge(i,j)==False):
            Grid.add_edge(i,j,key=1, length=float(math.sqrt((Grid.node[i]['xcoord']-Grid.node[j]['xcoord'])**2+(Grid.node[i]['ycoord']-Grid.node[j]['ycoord'])**2)), Type="Road")
        j=j+1
#connecting generators
for i in range(0,len(Grid.nodes)):
    if 'gen' in Grid.node[i]['name']:
        Grid.add_edge(i, list(Grid.neighbors(i))[0],key=1, length = 0, Type="Road")
nx.draw(Grid)
selected_edges = [(u,v) for u,v,e in Grid.edges(data=True) if e['Type'] == 'Road']
H = nx.Graph(selected_edges)
nx.draw(H)
Nodes = range(0,len(H))
RoadGrid = nx.Graph()
RoadGrid.add_nodes_from(Grid.nodes)
for i in Nodes:
    for j in Nodes:
        if Grid.has_edge(i,j,1):
            RoadGrid.add_edge(i,j,weight = Grid[i][j][1]['length'])
for i in Nodes:
    for j in Nodes:
        k=nx.shortest_path_length(RoadGrid, source = i, target = j, weight = 'weight')
        print([i,j,k])
#nx.write_gml(Grid, "Bus57WithData.gml")