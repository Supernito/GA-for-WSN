#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Sensor network lifetime's maximization using genetic algorythms
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

import random
from mst import msttree

SEED = 7
random.seed(SEED)
import genetics
import population
from os.path import dirname
from sys import argv

GENERATIONS = 200
POPULATION_SIZE = 200
SOLUTIONS = 1
MAP_FILENAME = raw_input("insert the name of the map file: ")

popul = population.create_population(MAP_FILENAME, POPULATION_SIZE)
popul[0] = msttree(popul[0])

for treeIndex in range(1, len(popul)):
    genetics.join_tree_randomly(popul[treeIndex])
for g in range(GENERATIONS):
    print ("Creating generation "), g + 1
    print "best: " + str(popul[0].lifetime)
    genetics.avaluation(popul)
    genetics.calc_sel_prob(popul)
    sons = genetics.operators(MAP_FILENAME, popul, g, GENERATIONS)
    popul = sons

genetics.avaluation(popul)
popul.sort(key=lambda x: x.lifetime, reverse=True)

# RESULTS WRITING#

if dirname(argv[0]):
    dst = dirname(argv[0]) + "/results/" + MAP_FILENAME[:-4] + ".res"
else:
    dst = "./results/" + MAP_FILENAME[:-4] + ".res"
print ("Saving results in"), dst
results_file = open(dst, 'w')
for s in range(SOLUTIONS):
    results_file.write("=============== SOLUTION ")
    results_file.write(str(s + 1))
    results_file.write(" ================")
    results_file.write("\n")
    for node in popul[s].nodes:
        if node.i == 0:
            continue
        results_file.write("Node ")
        results_file.write(str(node.i))
        results_file.write(" should send to node ")
        results_file.write(str(node.send_to))
        results_file.write("\n")
    results_file.write("Network lifetime ")
    results_file.write(str(popul[s].lifetime))
    results_file.write(" rounds")
    results_file.write("\n")
    results_file.write("\n")
results_file.close()
