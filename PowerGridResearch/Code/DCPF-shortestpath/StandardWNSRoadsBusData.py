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
Grid.add_node(0,name = "bus1", load = 0, productionmax = 200, xcoord = 2, ycoord=3)
Grid.add_node(1,name = "bus2", load = 21.7,productionmax = 80, xcoord = 4, ycoord = 1)
Grid.add_node(2,name = "bus3", load = 2.4,productionmax = 0, xcoord=3, ycoord=3)
Grid.add_node(3,name = "bus4", load = 7.6,productionmax = 0, xcoord =5,ycoord=3)
Grid.add_node(4,name = "bus5", load = 94.2,productionmax = 50, xcoord=9, ycoord=1)
Grid.add_node(5,name = "bus6", load = 0,productionmax = 0, xcoord=10, ycoord=4)
Grid.add_node(6,name = "bus7", load =22.8,productionmax = 0, xcoord = 10, ycoord=2)
Grid.add_node(7,name = "bus8", load =30,productionmax = 35, xcoord=16,ycoord=4)
Grid.add_node(8,name = "bus9", load = 0,productionmax = 0, xcoord=7, ycoord=7)
Grid.add_node(9,name = "bus10", load = 5.8,productionmax = 0, xcoord=8, ycoord=8)
Grid.add_node(10,name = "bus11", load = 0,productionmax = 30, xcoord=6, ycoord=7)
Grid.add_node(11,name = "bus12", load = 11.2,productionmax = 0, xcoord=4, ycoord=8)
Grid.add_node(12,name = "bus13", load = 0,productionmax = 40, xcoord=2, ycoord=8)
Grid.add_node(13,name = "bus14", load = 6.2,productionmax = 0, xcoord=3, ycoord=10)
Grid.add_node(14,name = "bus15", load = 8.2,productionmax = 0, xcoord=6, ycoord=15)
Grid.add_node(15,name = "bus16", load = 3.5,productionmax = 0, xcoord=7, ycoord=10)
Grid.add_node(16,name = "bus17", load = 9, productionmax = 0, xcoord=9, ycoord=12)
Grid.add_node(17,name = "bus18", load = 3.2,productionmax = 0, xcoord=10, ycoord=15)
Grid.add_node(18,name = "bus19", load=9.5,productionmax = 0, xcoord=15, ycoord=15)
Grid.add_node(19,name = "bus20", load = 2.2,productionmax = 0, xcoord=15, ycoord=14)
Grid.add_node(20,name = "bus21", load = 17.5,productionmax = 0, xcoord=16, ycoord=12)
Grid.add_node(21,name = "bus22", load = 0,productionmax = 0, xcoord=17, ycoord=10)
Grid.add_node(22,name = "bus23", load = 3.2,productionmax = 0, xcoord=12, ycoord=18)
Grid.add_node(23,name = "bus24", load = 8.7,productionmax = 0, xcoord=16, ycoord=18)
Grid.add_node(24,name = "bus25", load = 0,productionmax = 0, xcoord=14, ycoord=20)
Grid.add_node(25,name = "bus26", load = 3.5,productionmax = 0, xcoord=12, ycoord=20)
Grid.add_node(26,name = "bus27", load = 0,productionmax = 0, xcoord=11, ycoord=24)
Grid.add_node(27,name = "bus28", load = 0,productionmax = 0, xcoord=20, ycoord=24)
Grid.add_node(28,name = "bus29", load = 02.4,productionmax = 0, xcoord=3, ycoord=24 )
Grid.add_node(29,name = "bus30", load = 10.6,productionmax = 0, xcoord=3, ycoord=19)
#turn coords into position to make plotable
#bus 30 edges
Grid.add_edge(0,1, key=0, capacity = int(130), Type = "Power", Sus = float(16.64))
Grid.add_edge(0,2,key=0, capacity = int(130), Type = "Power", Sus = float(5.096))
Grid.add_edge(1,3,key=0, capacity = int(65), Type = "Power", Sus = float(5.197))
Grid.add_edge(2,3,key=0, capacity = int(130), Type = "Power", Sus = float(23.53))
Grid.add_edge(1,4,key=0, capacity = int(130), Type = "Power", Sus = float(4.77))
Grid.add_edge(1,5,key=0, capacity = int(65), Type = "Power", Sus = float(5.116))
Grid.add_edge(3,5,key=0, capacity = int(90), Type = "Power", Sus = float(22.31))
Grid.add_edge(4,6,key=0, capacity = int(70), Type = "Power", Sus = float(7.44))
Grid.add_edge(5,6,key=0, capacity = int(130), Type = "Power", Sus = float(11.02))
Grid.add_edge(5,7,key=0, capacity = int(32), Type = "Power", Sus = float(22.01))
Grid.add_edge(5,8,key=0, capacity = int(65), Type = "Power", Sus = float(4.807))
Grid.add_edge(5,9,key=0, capacity = int(32), Type = "Power", Sus = float(9.09))
Grid.add_edge(8,9,key=0, capacity = int(65), Type = "Power", Sus = float(3.906))
Grid.add_edge(8,10,key=0, capacity =int( 65), Type = "Power", Sus =float( 7.14))
Grid.add_edge(3,11,key=0, capacity =int( 65), Type = "Power", Sus = float(3.17))
Grid.add_edge(11,12,key=0, capacity = int(65), Type = "Power", Sus = float(6.1))
Grid.add_edge(11,13,key=0, capacity = int(32), Type = "Power", Sus = float(4.1))
Grid.add_edge(11,14,key=0, capacity = int(32), Type = "Power", Sus = float(2.25))
Grid.add_edge(11,15,key=0, capacity = int(32), Type = "Power", Sus = float(4.37))
Grid.add_edge(13,14,key=0, capacity = int(16), Type = "Power", Sus = float(2.25))
Grid.add_edge(15,16,key=0, capacity = int(16), Type = "Power", Sus = float(4.37))
Grid.add_edge(14,17,key=0, capacity = int(16), Type = "Power", Sus = float(3.69))
Grid.add_edge(17,18,key=0, capacity = int(16), Type = "Power", Sus = float(6.21))
Grid.add_edge(18,19,key=0, capacity = int(30), Type = "Power", Sus = float(11.764))
Grid.add_edge(9,19,key=0, capacity = int(32), Type = "Power", Sus = float(3.98))
Grid.add_edge(9,16,key=0, capacity = int(32), Type = "Power", Sus = float(10.31))
Grid.add_edge(9,20,key=0, capacity = int(32), Type = "Power", Sus = float(10.98))
Grid.add_edge(9,22,key=0, capacity = int(32), Type = "Power", Sus = float(5.400))
Grid.add_edge(20,21,key=0, capacity = int(32), Type = "Power", Sus = float(34.127))
Grid.add_edge(14,22,key=0, capacity = int(16), Type = "Power", Sus = float(3.97))
Grid.add_edge(21,23,key=0, capacity = int(16), Type = "Power", Sus = float(3.95))
Grid.add_edge(22,23,key=0, capacity = int(16), Type = "Power", Sus = float(2.989))
Grid.add_edge(23,24,key=0, capacity = int(16), Type = "Power", Sus = float(2.28))
Grid.add_edge(24,25,key=0, capacity = int(16), Type = "Power", Sus = float(1.871))
Grid.add_edge(24,26,key=0, capacity = int(16), Type = "Power", Sus = float(3.76))
Grid.add_edge(26,27,key=0, capacity = int(65), Type = "Power", Sus = float(2.71))
Grid.add_edge(26,28,key=0, capacity = int(16), Type = "Power", Sus = float(1.881))
Grid.add_edge(26,29,key=0, capacity = int(16), Type = "Power", Sus = float(1.293))
Grid.add_edge(28,29,key=0, capacity = int(16), Type = "Power", Sus = float(1.72))
Grid.add_edge(7,27,key=0, capacity = int(32), Type = "Power", Sus = float(4.54))
Grid.add_edge(5,27,key=0, capacity = int(32), Type = "Power", Sus = float(15.46))

  

#colouring nodes correctly--green is loaded node, red is buss, blue is generator
    #todo when I figure out why it's completely fucked trying to access datavalues

#code below was run once to generate a standard road network, then saved to file and commented out
#apply newman-watts-strogatz connectivity
NWS_k = 2
NWS_p=.03
DistanceDF = pd.DataFrame(columns = ['From', 'To', 'Distance'])
for i in range(0,30):
    for j in range(0,30):
        SquareX = (Grid.node[i]['xcoord']-Grid.node[j]['xcoord'])**2
        SquareY = (Grid.node[i]['ycoord']-Grid.node[j]['ycoord'])**2
        DistanceDF.loc[j+(i*30)] = [i,j, math.sqrt(SquareX+SquareY)]
#k connections        
for i in range(0,30):
    Subframe = DistanceDF.loc[DistanceDF['From']==i]
    Subframe = Subframe[Subframe.To != i]
    Subframe = Subframe[Subframe.To <=29]
    Connect = Subframe.nsmallest(NWS_k,'Distance')
    for index, row in Connect.iterrows():
        if (int(row['To']) != i) and (Grid.has_edge(i, int(row['To']))==False):
            Grid.add_edge(i, int(row['To']), key=1, length = float(row['Distance']), Type = "Road")
#p connections
for i in range(0,30):
    j=i
    while j < 30:
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
nx.write_gml(Grid, "Bus30WithDataMK2.gml")