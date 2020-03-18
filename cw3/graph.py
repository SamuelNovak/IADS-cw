import math

def euclid(p,q):
    x = p[0]-q[0]
    y = p[1]-q[1]
    return math.sqrt(x*x+y*y)
                
class Graph:

    # Complete as described in the specification, taking care of two cases:
    # the -1 case, where we read points in the Euclidean plane, and
    # the n>0 case, where we read a general graph in a different format.
    # self.perm, self.dists, self.n are the key variables to be set up.
    def __init__(self,n,filename):

        # Load the file as lines to be interpreted later
        lines = []
        with open(filename, "r") as f:
            # stripping whitespace and possible empty lines (preprocessing)
            for ln in f.readlines():
                ls = ln.strip()
                if ls:
                    # also convert to integers
                    ns = [int(i) for i in ls.split() if i]
                    lines.append(tuple(ns))
                    
            
        if n == -1: # Euclidean case
            self.n = len(lines)
            self.dists = [[0 for j in range(self.n)] for i in range(self.n)] # allocate table space
            for i in range(self.n):
                for j in range(i, self.n):
                    if i == j:
                        self.dists[i][j] = 0
                    else:
                        self.dists[i][j] = euclid(lines[i], lines[j])
                        self.dists[j][i] = self.dists[i][j]
                        
        else: # General case
            self.n = n
            self.dists = [[0 for j in range(self.n)] for i in range(self.n)] # allocate table space
            for i, j, w in lines:
                self.dists[i][j] = w
                self.dists[j][i] = w

        self.perm = list(range(self.n)) # initialize permutation, such that initially perm[i] = i
                
        for i in range(self.n):
            print(self.dists[i])

    # Complete as described in the spec, to calculate the cost of the
    # current tour (as represented by self.perm).
    def tourValue(self):
        # s = 0
        # for i in range(self.n-1):
        #     s += self.dists[self.perm[i]][self.perm[i+1]]
        # s += self.dists[self.perm[self.n-1]][self.perm[0]]
        # return s
        return sum([
            self.dists [self.perm[i]] [self.perm[(i+1) % self.n]]
            for i in range(self.n)]) # closely following the mathematical definition
    
    # Attempt the swap of cities i and i+1 in self.perm and commit
    # commit to the swap if it improves the cost of the tour.
    # Return True/False depending on success.
    def trySwap(self,i):
        w_original = self.tourValue() # store original weight
        i_original = self.perm[i] # for swapping
        self.perm[i] = self.perm[(i+1) % self.n]
        self.perm[(i+1) % self.n] = i_original

        w_new = self.tourValue()
        if w_new < w_original:
            return True
        else:
            self.perm[(i+1) % self.n] = self.perm[i]
            self.perm[i] = i_original
            return False

    # Consider the effect of reversiing the segment between
    # self.perm[i] and self.perm[j], and commit to the reversal
    # if it improves the tour value.
    # Return True/False depending on success.              
    def tryReverse(self,i,j):
        pass

    def swapHeuristic(self):
        better = True
        while better:
            better = False
            for i in range(self.n):
                if self.trySwap(i):
                    better = True

    def TwoOptHeuristic(self):
        better = True
        while better:
            better = False
            for j in range(self.n-1):
                for i in range(j):
                    if self.tryReverse(i,j):
                        better = True
                

    # Implement the Greedy heuristic which builds a tour starting
    # from node 0, taking the closest (unused) node as 'next'
    # each time.
    def Greedy(self):
        pass
    
