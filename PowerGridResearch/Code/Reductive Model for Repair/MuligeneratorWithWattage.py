# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:05:24 2018

@author: Brian French
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Generate_Graph import *
from Damage_Graph import *
from operator import itemgetter

Grid = GridWithRoadsWattage(3, 5, 15)