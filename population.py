#! /usr/bin/python2
# -*- coding: utf-8 -*-

#    Sensor network lifetime's maximization using genetic algorythms
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

import csv
from sys import argv
from os.path import dirname


class Node:
    """class node (sensor)"""

    def __init__(self, i, x, y, g):
        self.i = int(i)
        self.x = float(x)
        self.y = float(y)
        self.g_i_ = float(g)
        self.send_to = -1
        self.receive_from = []
        self.can_send_to = []
        self.energy_consumed = 0.0

    def __str__(self):
        return "%i" % self.i


class Tree:
    """class tree (network)"""

    def __init__(self):
        self.nodes = []
        self.lifetime = 0.0
        self.sel_prob = 0.0
        #selection probability
        self.acc_sel_prob = 0.0
        #accumulated selection probability


def create_nodes_list(map_filename):
    """creation of a list of nodes using a map file"""
    nodes_list = []
    n = 0
    if dirname(argv[0]):
        map_path = dirname(argv[0]) + "/maps/" + map_filename
    else:
        map_path = "./maps/" + map_filename

    with open(map_path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] and row[0].isdigit():
            #to avoid the first row and other wrong ones
                n += 1
                nodes_list.append(Node(row[0], row[1], row[2], row[3]))
    return nodes_list


def create_population(map_filename, ntrees):
    """creation of the population"""
    population = []
    for i in range(0, ntrees):
        t = Tree()
        #We want to create a new list, not a new reference
        t.nodes = create_nodes_list(map_filename)
        population.append(t)
    return population
