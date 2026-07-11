GA-for-WSN
==========

A genetic algorithm that maximizes the lifetime of a wireless sensor network by
evolving its routing tree (which node forwards its data to which). Written in
2012 as a final degree project; ported to Python 3 (and debugged) in 2026.

The energy model is the first-order radio model (Heinzelman et al.), and the
network lifetime is defined as the number of rounds until the first node runs
out of battery. Each individual encodes the tree as a parent pointer per node;
crossover and mutation only produce valid trees by construction.

Usage
-----

    python map_creator.py           # generate a random map in maps/
    python main.py test.map         # run the GA, writes results/test.res
    python ex_search.py test.map    # exhaustive search (small maps only),
                                    # writes results/test.exres

Map files live in `maps/` (CSV: node id, x, y, packets generated per round;
node 0 is the base station). `ex_search.py` brute-forces the true optimum so
GA results can be validated on small maps.

Requires Python 3, standard library only.

Note on historical results
--------------------------

The original 2012 `join()` stopped propagating `receive_from` bookkeeping
after the first ancestor whenever it moved a subtree with more than one node,
which under-counted relayed traffic and inflated reported lifetimes (shallow
trees like `test.map` were unaffected, which is why its result matched the
exhaustive optimum). Lifetime figures produced by the pre-2026 code on deeper
networks should be re-derived with the current version, which keeps the
bookkeeping consistent and only ever reports valid routing trees.
