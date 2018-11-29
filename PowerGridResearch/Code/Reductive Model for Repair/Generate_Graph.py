# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 10:09:01 2018

@author: Brian French
"""
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import grinpy as gp
def BasicGrid(subs, trans):
    NumSubstations=subs
    NumTransformers=trans
    #let generator be node zero
    Grid = nx.Graph()
    Grid.add_node(0, name="Generator", value=0, category="Generator", working = True)
    i=0
    while i<NumSubstations: #substations bridge generators to consumption nodes
       StrSubstation = "Substation_"+str(i)
       Grid.add_node(i+1, name = StrSubstation, value = 0, category = "Substation", working = True)
       Grid.add_edge(0,i+1, TravelTime=0, working = True)
       i=i+1
    i=0
    while i<NumTransformers: #tranformers supply a cluster of houses
        StrTransformer = "Transformer_"+str(i)
        Grid.add_node(NumSubstations+i+1, name = StrTransformer, value = 0, category = "Transformer", working = True)
        rand = random.randrange(1,NumSubstations+1)
        Grid.add_edge(rand,NumSubstations+i+1, TravelTime=0, working = True)
        i=i+1
    nx.draw(Grid)
    plt.show()
    print(list(nx.neighbors(Grid,0)))
    return Grid
def BasicGridWithRoads(subs,trans):
    NumSubstations=subs
    NumTransformers=trans
    #let generator be node zero
    Grid = nx.MultiGraph()
    Grid.add_node(0, name="Generator", value=0, category="Generator", working = True, colour = 'r')
    i=0
    while i<NumSubstations:
       StrSubstation = "Substation_"+str(i)
       Grid.add_node(i+1, name = StrSubstation, value = 0, category = "Substation", working = True, colour = 'm')
       Grid.add_edge(0,i+1, TravelTime=0, working = True, isPower = True, colour = 'b')
       i=i+1
    i=0
    while i<NumTransformers:
        StrTransformer = "Transformer_"+str(i)
        Grid.add_node(NumSubstations+i+1, name = StrTransformer, value = 0, category = "Transformer", working = True, colour = 'c')
        rand = random.randrange(1,NumSubstations+1)
        Grid.add_edge(rand,NumSubstations+i+1, TravelTime=0, working = True, isPower = True, colour = 'b')
        i=i+1
    
    #print(list(nx.neighbors(Grid,0)))
    i=0
    while i<(NumTransformers+NumSubstations):
        j=0
        IJNeighbors = False
        while j<=(NumTransformers+NumSubstations):  
            if i in Grid.neighbors(j):
                IJNeighbors = True
            if (Grid.node[i]['category']=="Generator") & (Grid.node[j]['category']=="Substation"):
                Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(5,2),0), colour = 'g')
            if (Grid.node[i]['category']=="Substation") & (Grid.node[j]['category']=="Substation"):
                Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(5,2),0), colour = 'g')
            if (Grid.node[i]['category']=="Transformer") & (Grid.node[j]['category']=="Substation") & (IJNeighbors):
                Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(5,2),0), colour = 'g')
            if (Grid.node[i]['category']=="Transformer") & (Grid.node[j]['category']=="Transformer"):
                randcheck = random.randrange(0,101)
                if randcheck<=10 : 
                    Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(15,5),0), colour = 'g')
            j=j+1
        i=i+1
    i=1
    nodecolourlist = ['r']
    while i<=NumSubstations:
        nodecolourlist.append('c')
        i=i+1
    while i<=(NumSubstations+NumTransformers):
        nodecolourlist.append('m')
        i=i+1
    nx.draw(Grid, node_color=nodecolourlist)
    plt.show()
    return Grid
def GridWithRoadsWattage(gens, subs, trans):
    NumSubstations=subs
    NumTransformers=trans
    NumGenerators = gens
    #let generator be node zero
    Grid = nx.MultiGraph()
    i=0
    while i<NumGenerators:
        StrGenerator = "Generator_"+str(i)    
        Grid.add_node(i, name=StrGenerator, value=0, category="Generator", working = True, colour = 'r', wattage = 500)
        i=i+1
    i=0
    while i<NumSubstations:
       StrSubstation = "Substation_"+str(i)
       Grid.add_node(i+NumGenerators, name = StrSubstation, value = 0, category = "Substation", working = True, colour = 'm')
       #OneOrTwo = random.randrange(0,2)
       #if OneOrTwo==0:
        #   Grid.add_edge(i+NumGenerators,random.randrange(0,NumGenerators+1), TravelTime=0, working = True, isPower = True, colour = 'b')
       #elif OneOrTwo == 1:
       ConnectedGenerators = random.sample(range(0,NumGenerators+1), 2)
       Grid.add_edge(i+NumGenerators,ConnectedGenerators[0], TravelTime=0, working = True, isPower = True, colour = 'b')
       Grid.add_edge(i+NumGenerators,ConnectedGenerators[1], TravelTime=0, working = True, isPower = True, colour = 'b')
       i=i+1
    i=0
    while i<NumTransformers:
        StrTransformer = "Transformer_"+str(i)
        Grid.add_node(NumSubstations+i+NumGenerators, name = StrTransformer, value = 0, category = "Transformer", working = True, colour = 'c')
        rand = random.randrange(NumGenerators,NumSubstations+NumGenerators+1)
        Grid.add_edge(rand,NumSubstations+i+NumGenerators, TravelTime=0, working = True, isPower = True, colour = 'b')
        i=i+1
    
    print(list(nx.neighbors(Grid,0)))
    
    print(list(nx.neighbors(Grid,1)))
    
    print(list(nx.neighbors(Grid,2)))
#    i=0
#    while i<(NumTransformers+NumSubstations):
#        j=0
#        IJNeighbors = False
#        while j<=(NumTransformers+NumSubstations):  
#            if i in Grid.neighbors(j):
#                IJNeighbors = True
#            if (Grid.node[i]['category']=="Generator") & (Grid.node[j]['category']=="Substation"):
#                Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(5,2),0), colour = 'g')
#            if (Grid.node[i]['category']=="Substation") & (Grid.node[j]['category']=="Substation"):
#                Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(5,2),0), colour = 'g')
#            if (Grid.node[i]['category']=="Transformer") & (Grid.node[j]['category']=="Substation") & (IJNeighbors):
#                Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(5,2),0), colour = 'g')
#            if (Grid.node[i]['category']=="Transformer") & (Grid.node[j]['category']=="Transformer"):
#                randcheck = random.randrange(0,101)
#                if randcheck<=10 : 
#                    Grid.add_edge(i,j,working=True, isPower=False, TravelTime = round(np.random.normal(15,5),0), colour = 'g')
#            j=j+1
#        i=i+1
    i=2
    nodecolourlist = ['r','r','r']
    while i<(NumSubstations+NumGenerators):
        nodecolourlist.append('c')
        i=i+1
    while i<(NumSubstations+NumTransformers+NumGenerators):
        nodecolourlist.append('m')
        i=i+1
    nx.draw(Grid, node_color=nodecolourlist)
    plt.show()
    return Grid
    