#! /usr/bin/python3
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

from os.path import dirname, splitext, basename, join
from sys import argv

import population
import genetics


def assign(slist, t):
    for x in range(1, len(t.nodes)):
        genetics.join(t, t.nodes[x], t.nodes[slist[x - 1]])


def add(l, size):
    """advance the send_to list to the next combination; True when done"""
    x = 0
    while x < size:
        if l[x] < size:
            l[x] += 1
            return False
        l[x] = 0
        x += 1
    return True


def is_cycle(l, size):
    """check if a send list makes a cycle"""
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


def search(map_filename):
    """try every send list and return the tree with the longest lifetime.
    A send list [x, y...] means that node 1 sends to x, node 2 to y..."""
    nodes_list_size = len(population.create_nodes_list(map_filename))
    send_list = [0] * (nodes_list_size - 1)
    best = population.Tree()
    while True:
        #the list must have at least one 0 (a link to the base station)
        if not is_cycle(send_list, nodes_list_size) and 0 in send_list:
            actual = population.Tree()
            actual.nodes = population.create_nodes_list(map_filename)
            assign(send_list, actual)
            #the same fitness the GA uses, so both tools stay comparable
            genetics.evaluation([actual])
            if actual.lifetime > best.lifetime:
                best = actual
        if add(send_list, nodes_list_size - 1):
            return best


if __name__ == "__main__":
    if len(argv) > 1:
        MAP_FILENAME = argv[1]
    else:
        MAP_FILENAME = input("insert the name of the map file: ")

    best = search(MAP_FILENAME)

    #RESULTS WRITING#
    name = splitext(basename(MAP_FILENAME))[0]
    dst = join(dirname(argv[0]) or ".", "results", name + ".exres")

    print("Saving results in", dst)
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
