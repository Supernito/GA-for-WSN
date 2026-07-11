#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Sensor network lifetime's maximization using genetic algorythms
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

import random
import math
import copy
import population

#crossover and (initial and final) mutation probabilities
CROSS_PROB = 0.8
MUT_PROB_INI = 0.0
MUT_PROB_END = 0.8
ELITISM = 2
#number of individuals that compete in each selection tournament
TOURNAMENT_SIZE = 3

#packet size in bits
M = 125 * 8
#energy dissipated to transmit or receive a single bit in nJ/bit
Eelec = 50
#reference distance where multi-path fadinf effects starts
D0 = 75
#Energy radiated to the wireless medium to transmit a single bit in distance 1
#far-field region in pJ/bit/m2
Efs = 10
#multi-path in pJ/bit/m4
Emp = 0.0013
#path-loss exponent
F_IN_MULTIPATH = 4
#battery in kJ
B = 15


def is_cicle(l):
    """checks if a list makes a cicle"""
    for e in l:
        if e.i == 0:
            continue
        e = l[e.send_to]
        done = []
        while e.send_to != 0 and e.send_to != -1 and not e.i in done:
            done.append(e.i)
            e = l[e.send_to]
        if e.i in done:
            return True
    return False


def refresh_can_send_list(t, n):
    """refresh the can_send_list of a node"""
    #all nodes except the ones in the receive_from set and himself
    return set(range(len(t.nodes))) - n.receive_from - {n.i}


def join(t, n1, n2):
    """join one node to another one"""
    #the subtree that moves with n1
    subtree = set(n1.receive_from)
    subtree.add(n1.i)
    #we change the destination node
    n1.send_to = t.nodes[n2.i].i
    #we need to refresh the receive_from set from the new parent
    #to the root (base station) with the subtree nodes
    node = n2
    done = set()
    while node.i != 0 and node.i not in done:
        node.receive_from |= subtree
        node.can_send_to = refresh_can_send_list(t, node)
        done.add(node.i)
        if node.send_to < 0:
            break
        node = t.nodes[node.send_to]


def unjoin(t, n):
    """unjoin one node and his parent"""
    #same as join but inverse
    subtree = set(n.receive_from)
    subtree.add(n.i)
    node = t.nodes[n.send_to]
    n.send_to = -1
    done = set()
    while node.i != 0 and node.i not in done:
        node.receive_from -= subtree
        node.can_send_to = refresh_can_send_list(t, node)
        done.add(node.i)
        if node.send_to < 0:
            break
        node = t.nodes[node.send_to]


def calc_energy(t, n):
    """calculation of the energy that the node wastes in a round"""
    d = math.sqrt((n.x - t.nodes[n.send_to].x) ** 2 + (n.y - t.nodes[n.send_to].y) ** 2)
    if d <= D0:
        ew = Efs
        f = 2
    else:
        ew = Emp
        f = F_IN_MULTIPATH
    return (n.g_i_ + 2 * len(n.receive_from)) * (Eelec * (10 ** -9)) * M + (n.g_i_ + len(n.receive_from)) * (
        ew * (10 ** -12)) * M * (d ** f)


def avaluation(popul):
    """calculation of the nodes energy wasted and the tree lifetime"""
    for t in popul:
        max_energy = 0.0
        for n in t.nodes:
            if n.i == 0:
                continue
            n.energy_consumed = calc_energy(t, n)
            if n.energy_consumed > max_energy:
                max_energy = n.energy_consumed
        t.lifetime = (B * (10 ** 3)) / max_energy


def join_tree_randomly(t):
    """creation of an initial random tree"""
    for n in t.nodes:
        if n.i == 0:
            continue
        n.can_send_to = refresh_can_send_list(t, n)
        join(t, n, t.nodes[random.choice(list(n.can_send_to))])


def select_parent(popul):
    """selection of a tree by tournament"""
    candidates = random.sample(popul, min(TOURNAMENT_SIZE, len(popul)))
    return max(candidates, key=lambda x: x.lifetime)


def crossover(map_filename, father, mother):
    """this function make the crossover between two trees"""
    son = population.Tree()
    son.nodes = population.create_nodes_list(map_filename)
    for node in son.nodes:
        crossed = False
        if node.i == 0:
            continue
        node.can_send_to = refresh_can_send_list(son, node)
        u = random.random()
        if u < 0.5:
            if father.nodes[node.i].send_to in node.can_send_to:
                #we chose farher and is selectable
                join(son, node, son.nodes[father.nodes[node.i].send_to])
                crossed = True
            elif mother.nodes[node.i].send_to in node.can_send_to:
                #we chose father but is not selectable, we cross with the mother
                join(son, node, son.nodes[mother.nodes[node.i].send_to])
                crossed = True
        else:
            #we chose mother and we do the same thing upside down
            if mother.nodes[node.i].send_to in node.can_send_to:
                join(son, node, son.nodes[mother.nodes[node.i].send_to])
                crossed = True
            elif father.nodes[node.i].send_to in node.can_send_to:
                join(son, node, son.nodes[father.nodes[node.i].send_to])
                crossed = True
        if not crossed:
            #a random one
            join(son, node, son.nodes[random.choice(list(node.can_send_to))])
    return son


def mutation(t):
    """mutation of a tree"""
    tree = copy.deepcopy(t)
    node = random.choice(tree.nodes)
    saved_dst = node.send_to
    #if node.can_send_to[] is size 1 we can't change the destination.
    # Changing the destination if its 0 can make no node send to 0
    if len(node.can_send_to) > 1 and node.send_to != 0:
        selectables = list(node.can_send_to)
        if node.send_to in selectables:
            selectables.remove(node.send_to)
        unjoin(tree, node)
        new_node = tree.nodes[random.choice(selectables)]
        join(tree, node, new_node)
        if is_cicle(tree.nodes):
            unjoin(tree, node)
            join(tree, node, tree.nodes[saved_dst])
    return tree


def operators(map_filename, popul, current_generation, total_generations):
    """aplication of genetic operators"""
    new_generation = []
    popul.sort(key=lambda x: x.lifetime, reverse=True)
    for i in range(0, ELITISM):
        new_generation.append(copy.deepcopy(popul[i]))
    #calculation of mutation probability (depending of generation)
    mut_prob = MUT_PROB_INI + (MUT_PROB_END - MUT_PROB_INI) * (float(current_generation) / (float(total_generations)))
    #operations
    for j in range(0, len(popul)):
        #crossover
        father = popul[j]
        u = random.random()
        if u < CROSS_PROB:
            mother = select_parent(popul)
            son = crossover(map_filename, father, mother)
        else:
            son = copy.deepcopy(father)
            #mutation
        for k in range(0, max(1, len(popul[0].nodes) // 10)):
            u = random.random()
            if u < mut_prob:
                son = mutation(son)
        #print j
        new_generation.append(son)
    avaluation(new_generation)
    new_generation.sort(key=lambda x: x.lifetime, reverse=True)
    new_generation = new_generation[:-ELITISM]
    return new_generation
