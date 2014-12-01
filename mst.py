#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Return the MST of a tree.
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

from genetics import join
from math import sqrt
from sys import maxint


def calcdst(nodea, nodeb, tree):
    return sqrt((tree.nodes[nodeb].x - tree.nodes[nodea].x) ** 2 + ((tree.nodes[nodeb].y - tree.nodes[nodea].y) ** 2))


#crea una lista de los nodos en la lista pasada y su más cercano
def makeclosestlist(chosennodes, tree):
    closestlist = []
    for chosenNode in chosennodes:
        nodea = chosenNode
        nodeb = -1
        bestdst = maxint
        for node in range(0, len(tree.nodes)):
            if chosenNode == node:
                continue
            dst = calcdst(chosenNode, node, tree)
            if dst < bestdst and not (nodea in chosennodes and node in chosennodes):
                nodeb = node
                bestdst = dst
        closestlist.append([nodea, nodeb, bestdst])
    return closestlist


#dada una lista de [nodeA, nodeB, dst], devuelve una lista con los dos nodos más cercanos [nodeA, nodeB]
def selectclosest(closestlist):
    bestdst = maxint
    nodea = -1
    nodeb = -1
    for e in closestlist:
        if e[2] < bestdst:
            nodea = e[0]
            nodeb = e[1]
            bestdst = e[2]
    return [nodea, nodeb]


def msttree(tree):
    chosennodes = [0]
    while len(chosennodes) < len(tree.nodes):
        closestlist = makeclosestlist(chosennodes, tree)
        closestchosen = selectclosest(closestlist)
        join(tree, tree.nodes[closestchosen[1]], tree.nodes[closestchosen[0]])
        chosennodes.append(closestchosen[1])
    return tree