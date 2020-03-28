import math
import graph
import enum

from random import randint
from itertools import permutations

# TODO
from sympy import Matrix, pprint

SMALL_THRESHOLD = 10

# GRAPH_TYPES = enum.Enum([
#     "GENERAL",
#     "METRIC",
#     "EUCLIDEAN"
# ])

# def generate_test(n:int, typ:GRAPH_TYPES, **kwargs):
#     """ Generate a test graph with n nodes."""
#     if n <= 5: # small graph (see paper)
#         if typ == GRAPH_TYPES.GENERAL:
#             return gen_small_general(n)
#         elif typ == GRAPH_TYPES.METRIC:
#             return gen_small_metric(n)
#         elif typ == GRAPH_TYPES.EUCLIDEAN:
#             return gen_small_euclidean(n, **kwargs)
#         else:
#             raise Exception("Invalid graph type requested.")
#     else:
#         return gen_big(n, typ)

def load_graph(euclidean:bool, par):
    """
    Create a Graph object, but skip the normal initialization
    (so no file reading will occur) and load the data given instead.

    Parameters:
    euclidean : bool - Specify input mode;
    par - if euclidean, this will be a list of points [(x,y),...]
          else this will be a distance matrix.
    """

    g = object.__new__(graph.Graph)
    g.n = len(par)
    if euclidean:
        g.dists = [[0 for j in range(g.n)] for i in range(g.n)]
        for i in range(g.n):
            for j in range(i+1, g.n):
                g.dists[i][j] = g.dists[j][i] = graph.euclid(par[i], par[j])
    else:
        # deep copy, just in case
        g.dists = [[par[i][j] for j in range(g.n)] for i in range(g.n)]
    g.perm = list(range(g.n))
    return g
        
def small_optimal_perm(g:graph.Graph):
    """
    Compute the optimal circuit in a small graph by enumeration.

    Return a tuple of (optimal weight, optimal permutation)
    """
    return min([
        (
            sum([
                g.dists [p[i]] [p[(i+1) % g.n]]
                for i in range(g.n)]),
            p
        )
        for p in permutations(g.perm)])



def gen_small_general(n, min_distance=1, max_distance=10):
    """
    Generates a small general (undirected => symmetric) graph
    (completely random weights) of size n (nodes).
    """
    dists = [[0 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i):
            dists[i][j] = randint(min_distance, max_distance)
            dists[j][i] = dists[i][j]

    g = load_graph(False, dists)
    opt_weight, opt_perm = small_optimal_perm(g)
    return g, opt_weight, opt_perm

    
def gen_small_metric(n):
    """
    Generates a metric graph of size n (nodes) by placing cities randomly
    on a plane and taking the Manhattan distance.
    """
    _, nodes, _, _ = gen_small_euclidean(n, 10, 10)
    dists = [[abs(nodes[i][0] - nodes[j][0]) + abs(nodes[i][1] - nodes[j][1])
              for j in range(n)] for i in range(n)]

    g = load_graph(False, dists)
    opt_weight, opt_perm = small_optimal_perm(g)
    return g, opt_weight, opt_perm


def gen_small_euclidean(n, width=100, height=100):
    """
    Generates a small Euclidean graph of size n (nodes) by randomly placing
    cities on a plane.
    """
    nodes = []
    while len(nodes) < n:
        u = (randint(0, width-1), randint(0, height-1))
        if u in nodes:
            continue # skip this one, because we already have it
        nodes.append(u)

    # now brute-force the optimal path
    g = load_graph(True, nodes)
    opt_weight, opt_perm = small_optimal_perm(g)
    
    return g, nodes, opt_weight, opt_perm


def random_isomorphic_graph(dists):
    n = len(dists)
    ret = [[0 for f in range(n)] for i in range(n)]
    # generate a random permutation
    unused = list(range(n))
    p = []
    while unused:
        p.append(unused.pop(randint(0, len(unused) - 1)))
    for i in range(n):
        for j in range(i):
            ret[p[i]][p[j]] = ret[p[j]][p[i]] = dists[i][j]
    return ret

def gen_big_general(n, min_distance=1, max_distance=10, low_cycle_threshold=5):
    """
    Generates a big general graph by planting a hidden good solution.
    It does this by generating a cycle of low weights and then swapping nodes around.
    """
    dists = [[0 for j in range(n)] for i in range(n)]
    for i in range(n):
        if i + 1 < n:
            dists[i][i+1] = dists[i+1][i] = randint(min_distance, low_cycle_threshold)
        for j in range(i+2, n):
            dists[i][j] = dists[j][i] = randint(low_cycle_threshold + 1, max_distance)

    opt_weight = sum([dists[i][(i+1) % n] for i in range(n)])
    dists = random_isomorphic_graph(dists)
    return load_graph(False, dists), opt_weight

def gen_big_metric(n):
    """
    Generates a big metric graph by creating a cicle (w.r.t. Manhattan metric).
    Can be also used to generate a Euclidean graph (so returns the points too).
    """
    R = n//2
    nodes = [(R + x, R + R - abs(x)) for x in range(-n//2, n//2, 2)] \
            + [(R + x, R - R + abs(x)) for x in range(n//2,
                                                      -n//2 + 1 - (1 if n % 2 == 0 else 0),
                                                      -2)]

    dists = [[abs(nodes[i][0] - nodes[j][0]) + abs(nodes[i][1] - nodes[j][1])
              for j in range(n)] for i in range(n)]
    opt_weight = sum([dists[i][j%n] for i,j in zip(range(n), range(1,n+1))])

    dists = random_isomorphic_graph(dists)
    return load_graph(False, dists), nodes, opt_weight

def gen_big_euclidean(n):
    """
    Generates a big euclidean graph, using gen_big_metric to generate the nodes.
    """
    _, nodes, _ = gen_big_metric(n)
    opt_weight = sum([graph.euclid(i, j) for i,j in zip(nodes, nodes[1:] + [nodes[0]])])

    rnodes = []
    while nodes:
        rnodes.append(nodes.pop(randint(0, len(nodes) - 1)))
        
    return load_graph(True, rnodes), opt_weight

DEFAULT_TESTS = [
    ("Swap", graph.Graph.swapHeuristic),
    ("TwoOpt", graph.Graph.TwoOptHeuristic),
    ("Swap, TwoOpt", graph.Graph.swapHeuristic, graph.Graph.TwoOptHeuristic),
    ("Greedy", graph.Graph.Greedy),
    ("NearestInsert", graph.Graph.NearestInsert)
]

def perform_tests(g:graph.Graph, opt_weight, tests=None):
    if not tests:
        # default
        tests = DEFAULT_TESTS

    g.perm = list(range(g.n)) # regenerate original permutation, just in case
        
    initial_value = g.tourValue()
    h_values = [-1 for i in range(len(tests))]
    for i in range(len(tests)):
        g.perm = list(range(g.n)) # regenerate the original permutation
        for f in tests[i][1:]:
            f(g) # run the heuristic
        h_values[i] = (g.tourValue())

    return initial_value, h_values

def table_row(g:graph.Graph, graph_type, opt_weight, tests=None):
    initial_value, h_values = perform_tests(g, opt_weight, tests)
    return [graph_type, g.n, opt_weight, initial_value] \
        + [(val, val/opt_weight, val/initial_value) for val in h_values]

def dec_places(x):
    if isinstance(x, float):
        return round(x, 3)
    else:
        return x

def row_as_latex(row):
    ret = ""
    for c in range(len(row)):
        if isinstance(row[c], tuple):
            ret += "\\shortstack{{ {} }}".format(" \\\\ ".join([str(i) for i in map(dec_places, row[c])]))
        else:
            ret += str(dec_places(row[c]))
        ret += (" & " if c < len(row) - 1 else " \\\\ \n\hline\n")
    return ret

def table_header_latex(tests=None):
    if not tests:
        tests = DEFAULT_TESTS

    ret = "\hline Type & $n$ & $W_0$ & $W_i$ "
    cols = 4
    for t in tests:
        ret += "& \\shortstack{{ {} \\\\ vs. $W_0$ \\\\ vs. $W_i$ }} ".format(t[0])
        cols += 1
    return (ret + "\\\\ \n \hline\hline\n", cols)

def run_multiple_tests(graph_type, N, n_min, n_max, tests=None):
    assert n_min >= 3, "n_min must be at least 3"
    if not tests:
        tests = DEFAULT_TESTS

    rows = []
    for n in range(n_min, n_max+1):
        for i in range(N):
            if n <= 7:
                if graph_type == "G":
                    g, o, _ = gen_small_general(n)
                elif graph_type == "M":
                    g, o, _ = gen_small_metric(n)
                elif graph_type == "E":
                    g, _, o, _ = gen_small_euclidean(n)
                else:
                    raise Exception("Only G (general), M (metric), E (euclidean) allowed as graph types.")
            else:
                if graph_type == "G":
                    g, o = gen_big_general(n)
                elif graph_type == "M":
                    g, _, o = gen_big_metric(n)
                elif graph_type == "E":
                    g, o = gen_big_euclidean(n)
                else:
                    raise Exception("Only G (general), M (metric), E (euclidean) allowed as graph types.")

            rows.append(table_row(g, graph_type, o))
    return rows

def avg_rows(rows):
    cols = len(rows[0])
    trans = [[None for i in range(len(rows))] for j in range(cols)]
    for i in range(len(rows)):
        for j in range(cols):
            trans[j][i] = rows[i][j]

    avgs = [("G" if "G" in trans[0] else "") \
        + ("M" if "M" in trans[0] else "") \
        + ("E" if "E" in trans[0] else "")]

    for c in range(1, cols):
        if isinstance(trans[c][0], tuple):
            avgs.append((
                sum([trans[c][i][1] for i in range(len(rows))])/len(rows),
                sum([trans[c][i][2] for i in range(len(rows))])/len(rows)
            ))
        else:
            avgs.append(
                sum([trans[c][i] for i in range(len(rows))])/len(rows)
            )
            
    return avgs


def test_all():
    rows = []
    for typ in ("G", "M", "E"):
        rows.append(avg_rows(run_multiple_tests(typ, 100, 5, 5)))
        rows.append(avg_rows(run_multiple_tests(typ, 100, 7, 7)))
        rows.append(avg_rows(run_multiple_tests(typ, 100, 10, 10)))
        rows.append(avg_rows(run_multiple_tests(typ, 100, 20, 20)))
        rows.append(avg_rows(run_multiple_tests(typ, 100, 50, 50)))

    # remove W_0, W_i columns in this case (because their avg make no sense)
    rows = map(lambda x: x[:2] + x[4:], rows)
    
    return rows
