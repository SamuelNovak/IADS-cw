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
            # allocate table space
            self.dists = [[0 for j in range(self.n)] for i in range(self.n)]
            for i in range(self.n):
                for j in range(i+1, self.n):
                    self.dists[i][j] = euclid(lines[i], lines[j])
                    self.dists[j][i] = self.dists[i][j]

        else: # General case
            self.n = n
            self.dists = [[0 for j in range(self.n)] for i in range(self.n)] # allocate table space
            for i, j, w in lines:
                self.dists[i][j] = w
                self.dists[j][i] = w

        self.perm = list(range(self.n)) # initialize permutation, such that initially perm[i] = i

        
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
        # self.dists[i][j] == self.dists[j][i] # symmetric matrix
        # so when we have (in the permutation) some nodes ..., a, b, c, d,...
        # and we swap b & c (so we get ..., a, c, b, d,...), we only need
        # to compare the distances (w(a,b) + w(c,d)) to (w(a,c) + w(b,d))
        # (where w is the weight function, repr. by self.dists)
        original = self.dists[self.perm[(i-1) % self.n]][self.perm[i]] \
            + self.dists[self.perm[(i+1) % self.n]][self.perm[(i+2) % self.n]]
        
        new = self.dists[self.perm[(i-1) % self.n]][self.perm[(i+1) % self.n]] \
            + self.dists[self.perm[i]][self.perm[(i+2) % self.n]]

        if new < original: # swap is better, perform it
            i_original = self.perm[i]
            self.perm[i] = self.perm[(i+1) % self.n]
            self.perm[(i+1) % self.n] = i_original
            return True
        else: # swap is not good, ignore it
            return False
            

    # Consider the effect of reversiing the segment between
    # self.perm[i] and self.perm[j], and commit to the reversal
    # if it improves the tour value.
    # Return True/False depending on success.              
    def tryReverse(self,i,j):
        # similarly to the Swap heuristic, the internal weights of some
        # subsequence won't be changed and we only need to compare the enpoints,
        # i.e. where the reversed subsequence touches the rest of the permutation

        # also, thanks to how the iteration is done in TwoOptHeuristic,
        # we can always assume i < j
        original = self.dists[self.perm[(i-1) % self.n]][self.perm[i]] \
            + self.dists[self.perm[j]][self.perm[(j+1) % self.n]]

        new = self.dists[self.perm[(i-1) % self.n]][self.perm[j]] \
            + self.dists[self.perm[i]][self.perm[(j+1) % self.n]]

        if new < original: # reverse is better, commit
            perm = list(self.perm[:])
            for k in range((j-i)//2+1):
                x = self.perm[i + k]
                perm[i + k] = self.perm[j - k]
                perm[j - k] = x

            self.perm = perm[:]
            return True
        else:
            return False

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
        # using a list of unused nodes
        # I originally wanted to have a list of booleans, but this is better,
        # because each individual search will be faster and the cost of removing
        # elements will be to some degree amortized
        # (it would be even more efficient with a linked list, keeping this as an idea for later)
        unused = list(range(1, self.n)) # starting at 0, so it's not unused
        self.perm[0] = 0
        for i in range(self.n-1): # n-1 because we want to be setting i+1 (i here is used just for iterating over the permutation)
            
            # argmin{j in unused} over distance from self.perm[i] to j
            minj = min(
                [(j, self.dists[self.perm[i]][j])
                 for j in unused], key=lambda x: x[1]
            )[0]
            
            self.perm[i+1] = minj
            unused.remove(minj)
            
    def NearestInsert(self):
        # find the two closest cities (arg min of edge weights) and start a tour from them
        ## \Theta(n^2)
        self.perm = list(
            min(
                [(i, j, self.dists[i][j]) # edge endpoints and its weight
                 for i in range(self.n)
                 for j in range(i)], # check only one direction, because it's symmetric
                key=lambda x: x[2]
            )[:2]
        )
        # generate a list of unused nodes
        ## \Theta(n)
        unused = [i for i in range(self.n) if i not in self.perm]

        # now keep adding the nearest neighbour of some node in self.perm from unused
        ## \Theta(n) * \Theta(n)
        while unused:
            # find nearest neighbour nn (arg min of edge weights over unused x self.perm)
            # also store for which node in self.perm this nn is the nearest neighbour
            ## \Theta(n)
            i, nn = min(
                [(i, pot_nn, self.dists[self.perm[i]][pot_nn])
                 for i in range(len(self.perm)) # because we will need the index in perm
                 for pot_nn in unused], # potential nearest neighbour
                key=lambda x: x[2]
            )[:2]
            # now decide which edge to replace (on which side of i to insert the nn)
            # \> the minimal distance of the two nodes adjacent to self.perm[i] to nn
            dist_before = self.dists[nn][self.perm[(i - 1) % len(self.perm)]]
            dist_after  = self.dists[nn][self.perm[(i + 1) % len(self.perm)]]
            if dist_before < dist_after:
                self.perm.insert(i, nn)
            else:
                self.perm.insert((i + 1) % len(self.perm), nn)
            unused.remove(nn)
