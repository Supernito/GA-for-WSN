#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Exhaustive search for a sensor network lifetime optimization
# Copyright (C) 2012  Juan "Nito" Pou  juanpou@ono.com
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

import copy
from os.path import dirname
from sys import argv

import population
import genetics

MAP_FILENAME = raw_input("insert de name of the map file: ")
#battery in kJ
B = 15


def calc_lifetime(t):
    """calculation of a tree's lifetime"""
    max_energy = 0.0
    for n in t.nodes:
        if n.i == 0:
            continue
        n.energy_consumed = genetics.calc_energy(t, n)
        if n.energy_consumed > max_energy:
            max_energy = n.energy_consumed
    t.lifetime = (B * (10 ** 3)) / max_energy


def assign(slist, t):
    for x in range(1, len(t.nodes)):
        genetics.join(t, t.nodes[x], t.nodes[slist[x - 1]])


def add(l, size):
    """move the send_to list to the next element"""
    global goOut
    x = 0
    while x < size:
        if l[x] < size:
            l[x] += 1
            break
        else:
            l[x] = 0
            x += 1
    if x == size:
        goOut = True


def is_cycle(l, size):
    """check if a list makes a cycle"""
    for dest in l:
        n = dest
        x = 0
        while x < size:
            if n == 0:
                break
            else:
                n = l[n - 1]
                x += 1
        if x == size:
            return True
    return False

#I'm going to make a list [x,y...] that means that node 1 
#sends to x, node 2 sends to y...
nodes_list = population.create_nodes_list(MAP_FILENAME)
send_list = []
best = population.Tree()
goOut = False
nodes_list_size = len(nodes_list)
for i in range(len(nodes_list) - 1):
    send_list.append(0)
while not goOut:
    if is_cycle(send_list, nodes_list_size) or 0 not in send_list:
        #list must have at least one 0
        add(send_list, nodes_list_size - 1)
        continue
    print ("Testing tree"), send_list
    actual = population.Tree()
    actual.nodes = population.create_nodes_list(MAP_FILENAME)
    assign(send_list, actual)
    calc_lifetime(actual)
    if actual.lifetime > best.lifetime:
        best = copy.copy(actual)
    add(send_list, nodes_list_size - 1)

#RESULTS WRITING#
if dirname(argv[0]):
    dst = dirname(argv[0]) + "/results/" + MAP_FILENAME[:-4] + ".exres"
else:
    dst = "./results/" + MAP_FILENAME[:-4] + ".exres"

print ("Saving results in"), dst
results_file = open(dst, 'w')
for node in best.nodes:
    if node.i == 0:
        continue
    results_file.write('Node ')
    results_file.write(str(node.i))
    results_file.write(' should send to node ')
    results_file.write(str(node.send_to))
    results_file.write('\n')
results_file.write('Network lifetime ')
results_file.write(str(best.lifetime))
results_file.write(' rounds')
results_file.write('\n')
results_file.write('\n')
results_file.close()
