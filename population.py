#! /usr/bin/python3
# -*- coding: utf-8 -*-

#    Sensor network lifetime's maximization using genetic algorithms
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
from os.path import dirname, basename, join


class Node:
    """class node (sensor)"""

    def __init__(self, i, x, y, g):
        self.i = int(i)
        self.x = float(x)
        self.y = float(y)
        self.g_i_ = float(g)
        self.send_to = -1
        self.receive_from = set()
        self.energy_consumed = 0.0

    def __str__(self):
        return "%i" % self.i


class Tree:
    """class tree (network)"""

    def __init__(self):
        self.nodes = []
        self.lifetime = 0.0


#parsed map rows, so crossover does not re-read the file for every child
_map_cache = {}


def map_path(map_filename):
    """path to a map, kept inside maps/ (basename strips any directory
    component so a crafted name cannot escape the folder)"""
    return join(dirname(argv[0]) or ".", "maps", basename(map_filename))


def _parse_map(map_filename):
    """read and validate a map file into (i, x, y, g) rows; node ids must be
    the contiguous 0..n-1 in row order, since the rest of the code uses the
    id as the position in Tree.nodes"""
    rows = []
    with open(map_path(map_filename), newline='') as csvfile:
        for lineno, row in enumerate(csv.reader(csvfile), 1):
            #skip the header, blank lines and any other non-data row
            if not row or not row[0].isdigit():
                continue
            if len(row) < 4:
                raise ValueError("%s line %d: expected 4 columns (id,x,y,g), got %d"
                                 % (map_filename, lineno, len(row)))
            try:
                rows.append((int(row[0]), float(row[1]), float(row[2]), float(row[3])))
            except ValueError:
                raise ValueError("%s line %d: non-numeric field in %r"
                                 % (map_filename, lineno, row))
    if not rows:
        raise ValueError("%s: no node rows found" % map_filename)
    for expected, row in enumerate(rows):
        if row[0] != expected:
            raise ValueError("%s: node ids must be 0..n-1 in order; expected %d, got %d"
                             % (map_filename, expected, row[0]))
    return rows


def create_nodes_list(map_filename):
    """creation of a list of nodes using a map file"""
    if map_filename not in _map_cache:
        _map_cache[map_filename] = _parse_map(map_filename)
    return [Node(i, x, y, g) for (i, x, y, g) in _map_cache[map_filename]]


def create_population(map_filename, ntrees):
    """creation of the population"""
    population = []
    for i in range(0, ntrees):
        t = Tree()
        #We want to create a new list, not a new reference
        t.nodes = create_nodes_list(map_filename)
        population.append(t)
    return population
