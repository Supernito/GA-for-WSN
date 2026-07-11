#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Sensor network lifetime's maximization using genetic algorithms
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
from os.path import dirname, splitext
from sys import argv

GENERATIONS = 200
POPULATION_SIZE = 200
SOLUTIONS = 1


def run(map_filename, generations=GENERATIONS, population_size=POPULATION_SIZE):
    """run the whole GA and return the population sorted by lifetime"""
    popul = population.create_population(map_filename, population_size)
    popul[0] = msttree(popul[0])
    for treeIndex in range(1, len(popul)):
        genetics.join_tree_randomly(popul[treeIndex])
    #operators() already evaluates every new generation, so we only need
    #to evaluate (and sort, so the "best" print is right) the initial one
    genetics.evaluation(popul)
    popul.sort(key=lambda x: x.lifetime, reverse=True)
    for g in range(generations):
        print("Creating generation", g + 1)
        print("best: " + str(popul[0].lifetime))
        popul = genetics.operators(map_filename, popul, g, generations)
    popul.sort(key=lambda x: x.lifetime, reverse=True)
    return popul


if __name__ == "__main__":
    if len(argv) > 1:
        MAP_FILENAME = argv[1]
    else:
        MAP_FILENAME = input("insert the name of the map file: ")

    popul = run(MAP_FILENAME)

    # RESULTS WRITING#

    if dirname(argv[0]):
        dst = dirname(argv[0]) + "/results/" + splitext(MAP_FILENAME)[0] + ".res"
    else:
        dst = "./results/" + splitext(MAP_FILENAME)[0] + ".res"
    print("Saving results in", dst)
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
