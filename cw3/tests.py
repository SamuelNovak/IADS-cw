import math
import graph
import enum

from random import randint


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

def gen_small_general(n, min_distance=1, max_distance=10):
    dists = [[0 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i):
            dists[i][j] = randint(min_distance, max_distance)
            dists[j][i] = dists[i][j]
    for ln in dists:
        print(ln)
    return dists
    
def gen_small_metric(n, min_distance=1, max_distance=10):
    dists = [[0 for j in range(n)] for i in range(n)]
    dists[0][1] = dists[1][0] = randint(min_distance, max_distance)
    for i in range(2, n): # starting from node 2
        
    
    for ln in dists:
        print(ln)
    return dists

def gen_small_euclidean(n, width=100, height=100):
    nodes = []
    while len(nodes) < n:
        u = (randint(0, width-1), randint(0, height-1))
        if u in nodes:
            continue # skip this one, because we already have it
        nodes.append(u)
    return nodes

def gen_big():
    pass
