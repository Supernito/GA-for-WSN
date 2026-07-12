#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Regression tests for the sensor network lifetime GA.
# Run with: python test_ga.py

import contextlib
import copy
import io
import os
import random
import sys
import unittest

#resolve maps/ relative to this file no matter where the tests run from
sys.argv[0] = os.path.abspath(__file__)

import ex_search
import genetics
import main
import population
from mst import msttree


def build_random_tree(map_filename):
    tree = population.create_population(map_filename, 1)[0]
    genetics.join_tree_randomly(tree)
    return tree


def true_descendants(tree):
    """descendant sets recomputed from send_to alone, independently of the
    incremental receive_from bookkeeping"""
    desc = {n.i: set() for n in tree.nodes}
    for n in tree.nodes:
        if n.i == 0:
            continue
        cur = tree.nodes[n.send_to]
        steps = 0
        while True:
            desc[cur.i].add(n.i)
            if cur.i == 0 or cur.send_to < 0:
                break
            cur = tree.nodes[cur.send_to]
            steps += 1
            if steps > len(tree.nodes):
                raise AssertionError("cycle found walking up from node %d" % n.i)
    return desc


def is_valid(tree):
    """every node must reach the base station without cycles"""
    for n in tree.nodes:
        if n.i == 0:
            continue
        seen = set()
        cur = n
        while cur.i != 0:
            if cur.i in seen or cur.send_to < 0:
                return False
            seen.add(cur.i)
            cur = tree.nodes[cur.send_to]
    return True


def check_bookkeeping(testcase, tree):
    desc = true_descendants(tree)
    for n in tree.nodes:
        #the base station's receive_from is intentionally not maintained
        #(join stops its walk there and nothing ever reads it)
        if n.i == 0:
            continue
        testcase.assertEqual(n.receive_from, desc[n.i],
                             "receive_from drifted on node %d" % n.i)


class TestBookkeeping(unittest.TestCase):
    def test_random_trees_are_valid(self):
        random.seed(1)
        for _ in range(20):
            tree = build_random_tree('val15.map')
            self.assertTrue(is_valid(tree))
            check_bookkeeping(self, tree)

    def test_mutation_keeps_invariants(self):
        random.seed(2)
        tree = build_random_tree('val15.map')
        for _ in range(300):
            genetics.mutation(tree)
        self.assertTrue(is_valid(tree))
        check_bookkeeping(self, tree)

    def test_crossover_keeps_invariants(self):
        random.seed(3)
        father = build_random_tree('val15.map')
        mother = build_random_tree('val15.map')
        for _ in range(20):
            son = genetics.crossover('val15.map', father, mother)
            self.assertTrue(is_valid(son))
            check_bookkeeping(self, son)

    def test_mst_seed_is_valid_and_mutable(self):
        #regression: mutation used to silently no-op on MST-built nodes
        #because msttree never initialized the old cached can_send_to
        random.seed(4)
        tree = msttree(population.create_population('test.map', 1)[0])
        self.assertTrue(is_valid(tree))
        check_bookkeeping(self, tree)
        trials = 300
        changed = 0
        before = [n.send_to for n in tree.nodes]
        for _ in range(trials):
            clone = copy.deepcopy(tree)
            genetics.mutation(clone)
            #a mutation must never leave the tree invalid or its bookkeeping drifted
            self.assertTrue(is_valid(clone))
            check_bookkeeping(self, clone)
            if [n.send_to for n in clone.nodes] != before:
                changed += 1
        self.assertGreater(changed / trials, 0.25)


class TestEvaluation(unittest.TestCase):
    def test_relayed_matches_descendants(self):
        #calc_relayed (the sigma(i) pass) must equal the sum of g over the
        #real descendants of each node
        random.seed(5)
        for _ in range(10):
            tree = build_random_tree('val15.map')
            relayed = genetics.calc_relayed(tree)
            desc = true_descendants(tree)
            for n in tree.nodes:
                expected = sum(tree.nodes[i].g_i_ for i in desc[n.i])
                self.assertAlmostEqual(relayed[n.i], expected)

    def test_relayed_is_g_weighted_not_a_count(self):
        #het7.map has g != 1, so relayed traffic (sum of g) must differ from
        #the plain descendant count -- this is what distinguishes the
        #heterogeneous sigma(i) fix from the old len(receive_from)
        random.seed(50)
        distinguished = False
        for _ in range(10):
            tree = build_random_tree('het7.map')
            relayed = genetics.calc_relayed(tree)
            desc = true_descendants(tree)
            for n in tree.nodes:
                expected = sum(tree.nodes[i].g_i_ for i in desc[n.i])
                self.assertAlmostEqual(relayed[n.i], expected)
                if abs(expected - len(desc[n.i])) > 1e-9:
                    distinguished = True
        #guard against the fixture silently reverting to all-g=1
        self.assertTrue(distinguished,
                        "het7.map must exercise g != 1 for this test to bite")

    def test_lifetime_is_positive(self):
        random.seed(6)
        tree = build_random_tree('val15.map')
        genetics.evaluation([tree])
        self.assertGreater(tree.lifetime, 0.0)


class TestOperators(unittest.TestCase):
    def test_best_never_gets_worse(self):
        #elitism must make the best lifetime monotonically non-decreasing
        #and keep the population size constant
        random.seed(7)
        popul = population.create_population('val15.map', 30)
        popul[0] = msttree(popul[0])
        for i in range(1, len(popul)):
            genetics.join_tree_randomly(popul[i])
        genetics.evaluation(popul)
        best = max(t.lifetime for t in popul)
        for g in range(10):
            popul = genetics.operators('val15.map', popul, g, 10)
            self.assertEqual(len(popul), 30)
            self.assertGreaterEqual(popul[0].lifetime, best)
            best = popul[0].lifetime
            #every bred individual must be valid, not just the elite on top
            for t in popul:
                self.assertTrue(is_valid(t))
                check_bookkeeping(self, t)


class TestOptimum(unittest.TestCase):
    """the GA must find the exhaustive-search optimum on small maps"""

    def ga_matches_exhaustive(self, map_filename):
        optimum = ex_search.search(map_filename)
        random.seed(main.SEED)
        with contextlib.redirect_stdout(io.StringIO()):
            popul = main.run(map_filename)
        self.assertTrue(is_valid(popul[0]))
        self.assertAlmostEqual(popul[0].lifetime, optimum.lifetime,
                               delta=optimum.lifetime * 1e-9)

    def test_test_map(self):
        self.ga_matches_exhaustive('test.map')

    def test_val6_map(self):
        self.ga_matches_exhaustive('val6.map')

    def test_val7_map(self):
        self.ga_matches_exhaustive('val7.map')

    def test_het7_map(self):
        #heterogeneous g(i): the GA must reach the true optimum end-to-end
        self.ga_matches_exhaustive('het7.map')


if __name__ == '__main__':
    unittest.main(verbosity=2)
