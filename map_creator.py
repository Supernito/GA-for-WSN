#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Map creator for ensor network lifetime's maximization
#    Copyright (C) 2012  Juan "Nito" Pou  juanpou@ono.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


#This is the program to generate random maps.
#Base station is assumed to be the first node found
#Maps are saved in the 'maps' folder that must exist where this file is

import csv
from random import uniform
from os.path import dirname
from sys import argv

#Map dimension
MAX_X = 1000
MAX_Y = 1000
MAX_G_i_ = 5

#Number of nodes
NODES = input("Number of nodes: ")
#Name of the map file 
MAP_FILE_NAME = raw_input("Map file name (if exists will be deleted): ")

if dirname(argv[0]):
    dst = "./maps/" + MAP_FILE_NAME
else:
    dst = "./maps/" + MAP_FILE_NAME

MAP_FILE = csv.writer(open(dst, "wb"))
MAP_FILE.writerow(["Node number", "X", "Y", "g(i)"])
#Base station creation
MAP_FILE.writerow(["0", "0", "500", "0"])

for i in range(1, NODES + 1):
    #homogeneus networks
    MAP_FILE.writerow([i, uniform(0, MAX_X), uniform(0, MAX_Y), "1"])
    #heterogeneous networks
    #MAP_FILE.writerow([i,uniform(0, MAX_X),uniform(0, MAX_Y),uniform(0, MAX_G_i_)])
