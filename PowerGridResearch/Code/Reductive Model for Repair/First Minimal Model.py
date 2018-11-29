# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 10:04:18 2018

@author: Brian French
"""
#importing packages to be used 
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Generate_Graph import *
from Damage_Graph import *


#constructors for grid. Grid will be treated as 3 tier, production/distribution/consumption nodes
Grid = BasicGridWithRoads(3,20) #define a grid with 1 generator, 6 substations, and 80 nodes
print(Grid.nodes())
BrokenGrid = DamageGraph(Grid) #apply the break function across the grid
print(list(BrokenGrid.nodes(data=True)))
print(list(BrokenGrid.edges))