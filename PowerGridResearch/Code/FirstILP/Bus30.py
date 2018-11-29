# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 10:08:13 2018

@author: Brian French
"""

#hardcoding bus30--loads taken from http://motor.ece.iit.edu/Data/tgplan30.doc
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import grinpy as gp
def IEEE30():
    Grid = nx.Graph()
    #apply coordinates from http://pubs.sciepub.com/ajeee/4/3/4/figure/5 with a best guess taken from looking at it and overlaying a grid
    Grid.add_node(0,name = "bus1", load = 0, xcoord = 2, ycoord=3)
    Grid.add_node(1,name = "bus2", load = .08, xcoord = 4, ycoord = 1)
    Grid.add_node(2,name = "bus3", load = .01, xcoord=3, ycoord=3)
    Grid.add_node(3,name = "bus4", load = .20, xcoord =5,ycoord=3)
    Grid.add_node(4,name = "bus5", load = .12, xcoord=9, ycoord=1)
    Grid.add_node(5,name = "bus6", load = 0, xcoord=10, ycoord=4)
    Grid.add_node(6,name = "bus7", load =.08, xcoord = 10, ycoord=2)
    Grid.add_node(7,name = "bus8", load =.1, xcoord=16,ycoord=4)
    Grid.add_node(8,name = "bus9", load = 0, xcoord=7, ycoord=7)
    Grid.add_node(9,name = "bus10", load = .07, xcoord=8, ycoord=8)
    Grid.add_node(10,name = "bus11", load = 0, xcoord=6, ycoord=7)
    Grid.add_node(11,name = "bus12", load = .08, xcoord=4, ycoord=8)
    Grid.add_node(12,name = "bus13", load = 0, xcoord=2, ycoord=8)
    Grid.add_node(13,name = "bus14", load = .02, xcoord=3, ycoord=10)
    Grid.add_node(14,name = "bus15", load = .03, xcoord=6, ycoord=15)
    Grid.add_node(15,name = "bus16", load = .01, xcoord=7, ycoord=10)
    Grid.add_node(16,name = "bus17", load = .03, xcoord=9, ycoord=12)
    Grid.add_node(17,name = "bus18", load = .01, xcoord=10, ycoord=15)
    Grid.add_node(18,name = "bus19", load=.02, xcoord=15, ycoord=15)
    Grid.add_node(19,name = "bus20", load = .01, xcoord=15, ycoord=14)
    Grid.add_node(20,name = "bus21", load = .06, xcoord=16, ycoord=12)
    Grid.add_node(21,name = "bus22", load = 0, xcoord=17, ycoord=10)
    Grid.add_node(22,name = "bus23", load = .01, xcoord=12, ycoord=18)
    Grid.add_node(23,name = "bus24", load = .02, xcoord=16, ycoord=18)
    Grid.add_node(24,name = "bus25", load = 0, xcoord=14, ycoord=20)
    Grid.add_node(25,name = "bus26", load = .01, xcoord=12, ycoord=20)
    Grid.add_node(26,name = "bus27", load = 0, xcoord=11, ycoord=24)
    Grid.add_node(27,name = "bus28", load = 0, xcoord=20, ycoord=24)
    Grid.add_node(28,name = "bus29", load = 0, xcoord=3, ycoord=24 )
    Grid.add_node(29,name = "bus30", load = .02, xcoord=3, ycoord=19)
    Grid.add_node(30,name = "gen1", production = 20, xcoord = 3.1, ycoord = 19.1)
    Grid.add_node(31, name = "gen2", production = 20, xcoord = 16.1, ycoord=18.1)
    Grid.add_node(32, name = "gen3", production = 20, xcoord=6.1, ycoord=7.1)
    Grid.add_node(33, name = "gen4", production = 80, xcoord=4.1, ycoord=1.1)
    Grid.add_node(34, name = "gen5", production = 50, xcoord=16.1, ycoord=4.1)
    Grid.add_node(35, name = "gen6", production = 50, xcoord=9.1, ycoord=1.1)
    Grid.add_node(36, name = "gen7", production = 100, xcoord=2.1, ycoord=3.1)
    #turn coords into position to make plotable
    for j in Grid.nodes:
        Grid.node[j]['pos'] = (Grid.node[j]['xcoord'],Grid.node[j]['ycoord'])
    #bus 30 edges
    Grid.add_edge(0,1, capacity = 30)
    Grid.add_edge(0,2, capacity = 30)
    Grid.add_edge(1,3, capacity = 30)
    Grid.add_edge(2,3, capacity = 30)
    Grid.add_edge(1,4, capacity = 30)
    Grid.add_edge(1,5, capacity = 30)
    Grid.add_edge(3,5, capacity = 30)
    Grid.add_edge(4,6, capacity = 30)
    Grid.add_edge(5,6, capacity = 30)
    Grid.add_edge(5,7, capacity = 30)
    Grid.add_edge(5,8, capacity = 30)
    Grid.add_edge(5,9, capacity = 30)
    Grid.add_edge(8,9, capacity = 30)
    Grid.add_edge(8,10, capacity = 30)
    Grid.add_edge(3,11, capacity = 65)
    Grid.add_edge(11,12, capacity = 65)
    Grid.add_edge(11,13, capacity = 32)
    Grid.add_edge(11,14, capacity = 32)
    Grid.add_edge(11,15, capacity = 32)
    Grid.add_edge(13,14, capacity = 16)
    Grid.add_edge(15,16, capacity = 16)
    Grid.add_edge(14,17, capacity = 16)
    Grid.add_edge(17,18, capacity = 16)
    Grid.add_edge(18,19, capacity = 30)
    Grid.add_edge(9,19, capacity = 32)
    Grid.add_edge(9,16, capacity = 32)
    Grid.add_edge(9,20, capacity = 30)
    Grid.add_edge(9,22, capacity = 30)
    Grid.add_edge(20,21, capacity = 30)
    Grid.add_edge(14,22, capacity = 16)
    Grid.add_edge(21,23, capacity = 30)
    Grid.add_edge(22,23, capacity = 16)
    Grid.add_edge(23,24, capacity = 30)
    Grid.add_edge(24,25, capacity = 30)
    Grid.add_edge(24,26, capacity = 30)
    Grid.add_edge(26,27, capacity = 30)
    Grid.add_edge(26,28, capacity = 30)
    Grid.add_edge(26,29, capacity = 30)
    Grid.add_edge(28,29, capacity = 30)
    Grid.add_edge(7,27, capacity = 30)
    Grid.add_edge(5,27, capacity = 30)
    
    #connecting generators to the correct node
    
    Grid.add_edge(30,29, capacity = 40)
    Grid.add_edge(31,23, capacity = 40)
    Grid.add_edge(32,10, capacity = 40)
    Grid.add_edge(33,1, capacity = 160)
    Grid.add_edge(34,7, capacity = 100)
    Grid.add_edge(35,4, capacity = 100)
    Grid.add_edge(36,0, capacity = 200)
    
    #colouring nodes correctly--green is loaded node, red is buss, blue is generator
        #todo when I figure out why it's completely fucked trying to access datavalues
    nx.draw(Grid)
    plt.show()
    return Grid