# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 09:45:48 2018

@author: Brian French
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Generate_Graph import *
from Damage_Graph import *
from operator import itemgetter

Grid = BasicGridWithRoads(3,20)
BestSolution = []
SecondBestSolution = []
ThirdBestSolution = []
i = 0
NumberOfCases = 0
while i <= NumberOfCases:
    BrokenGrid = TwoNodeBreak(Grid)
    JustRoads=nx.Graph( [ (u,v,d) for u,v,d in Grid.edges(data=True) if d['isPower']==False] )
    JustRoads.add_nodes_from(Grid.nodes(data=True))
    print(list(JustRoads.edges(data=True)))
    ToVisit = [x for x,y in JustRoads.nodes(data=True) if y['working']==False]
    nx.draw(JustRoads)
    plt.show()
    print(list(ToVisit))
    jlengths = []
    jnames = []
    j=0
    while j<len(JustRoads.nodes()):
       home = j
       path1 = nx.shortest_path_length(JustRoads, home, ToVisit[0], 'TravelTime')
       path2 = nx.shortest_path_length(JustRoads, home, ToVisit[1], 'TravelTime')
       path3 = nx.shortest_path_length(JustRoads, ToVisit[0], ToVisit[1] , 'TravelTime')
       shortpathlength = min([path1+path3+path2, 2*(path1+path2)])
       if shortpathlength == (path1+path2+path3):
           shortpath = nx.shortest_path(JustRoads, home, ToVisit[0], 'TravelTime')+nx.shortest_path(JustRoads, ToVisit[0], ToVisit[1] , 'TravelTime')+nx.shortest_path(JustRoads, ToVisit[1], home , 'TravelTime')
       elif shortpathlength == (2*(path1+path2)):
           shortpath = nx.shortest_path(JustRoads, home, ToVisit[0], 'TravelTime')+nx.shortest_path(JustRoads,ToVisit[0], home, 'TravelTime')+nx.shortest_path(JustRoads, home, ToVisit[1], 'TravelTime')+nx.shortest_path(JustRoads, ToVisit[1], home, 'TravelTime')
       else:
           print("this wasn't supposed to happen, check simple resilience code")
           print(home)
           print(ToVisit)
       jnames.append(shortpath)
       jlengths.append(shortpathlength)
       j = j+1
    i = i+1
print(jnames)
print(jlengths)
#index = 