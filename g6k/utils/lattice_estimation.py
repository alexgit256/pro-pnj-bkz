#!/usr/bin/env python
# -*- coding: utf-8 -*-


from math import e, lgamma, log, pi

from fpylll import BKZ as fplll_bkz, GSO, IntegerMatrix, LLL
from fpylll.tools.bkz_simulator import simulate
from fpylll.util import gaussian_heuristic

from g6k.algorithms.bkz import default_dim4free_fun
from g6k.utils.util import load_latticechallenge_randomly
from random import randint
from fpylll.algorithms.bkz2 import BKZReduction


#estimation for lattice challenge

def delta_0f(k):
    """
    Auxiliary function giving root Hermite factors. Small values
    experimentally determined, otherwise from [Chen13]

    :param k: BKZ blocksize for which the root Hermite factor is required

    """
    small = (( 2, 1.02190),  # noqa
             ( 5, 1.01862),  # noqa
             (10, 1.01616),
             (15, 1.01485),
             (20, 1.01420),
             (25, 1.01342),
             (28, 1.01331),
             (40, 1.01295))

    k = float(k)
    if k <= 2:
        return (1.0219)
    elif k < 40:
        for i in range(1, len(small)):
            if small[i][0] > k:
                return (small[i-1][1])
    elif k == 40:
        return (small[-1][1])
    else:
        return (k/(2*pi*e) * (pi*k)**(1./k))**(1/(2*(k-1.)))


def log_gh_svp(d, delta_bkz, svp_dim,n, q):
    """
    Calculates the log of the Gaussian heuristic of the context in which
    SVP will be ran to try and discover the projected embedded error.

    The volume component of the Gaussian heuristic (in particular the lengths
    of the appropriate Gram--Schmidt vectors) is estimated using the GSA
    [Schnorr03] with the multiplicative factor = delta_bkz ** -2.

    NB, here we use the exact volume of an n dimensional sphere to calculate
    the ``ball_part`` rather than the usual approximation in the Gaussian
    heuristic.

    :param d: the dimension of the lattice = m
    :param delta_bkz: the root Hermite factor given by the BKZ reduction
    :param svp_dim: the dimension of the SVP call in context [d-svp_dim:d]
    :param n:  dimension of the qI
    :param q: the modulus of the lattice instance

    """
    d = float(d)
    svp_dim = float(svp_dim)
    ball_part = ((1./svp_dim)*lgamma((svp_dim/2.)+1))-(.5*log(pi))
    vol_part = ((1./d)*n*log(q))+((svp_dim-d)*log(delta_bkz))
    return ball_part + vol_part


def gsa_params(m, q, decouple=False):
    """
    Finds winning parameters (a BKZ reduction dimension and a final SVP call
    dimension) for a given Darmstadt lattice instance (n, alpha).
    
    :param m: Challenge lattice dimension m
    :param q: q is equal to n, the modulus of the lattice instance. ``None``   
              means  determine by reloading the challenge
    :param samples: maximum number of lattice samples to use for the embedding
        lattice. ``None`` means ``5*n``
    :param d: find best parameters for a dimension ``d`` embedding lattice
    :param decouple: if True the BKZ dimension and SVP dimension may differ

    """
    if q is None:
        _, _, q = load_latticechallenge(m)

    params = decoupler(decouple, q, m)
    min_cost_param = find_min_complexity(params)
    if min_cost_param is not None:
        return min_cost_param


def decoupler(decouple, q, d):
    """
    Creates valid (bkz_dim, svp_dim, d) triples, as determined by
    ``primal_parameters`` and determines which succeed in finding the shortest vector for lattice instance.

    :param decouple: if True the BKZ dimension and SVP dimension may differ
    :param q: q is equal to n, the modulus of the lattice instance. ``None``   
              means  determine by reloading the challenge
    :param d: find best parameters for dimension ``d`` embedding lattice
    
    return [bkz_block_size, svp_dim, m] m = d, the number of rows in solvable lattice instance.

    """
    params = []

    # if d is not None:
    #     ms = [d]
    # else:
    #     ms = range(n, min(5*n, samples))
    n = q #dimension of qI
    for m in range(2*n,d+1):
        beta_bound = min(m, 200+default_dim4free_fun(200))
        svp_bound = min(m, 200)
        for bkz_block_size in range(40, beta_bound):
            delta_0 = delta_0f(bkz_block_size)
            if decouple:
                svp_dims = range(40, svp_bound)
            else:
                svp_dims = [min(bkz_block_size, svp_bound)]

            for svp_dim in svp_dims:
                rhs = log_gh_svp(m, delta_0, svp_dim, q, q)
                
                if log(1.*svp_dim/d)/2.+log(q) > rhs  + log(svp_dim)/2. : #sqrt(dsvp/d)*target_norm >= GH on projected dsvp-dimensional reduced lattice with delta(beta).
                    # print(m,bkz_block_size, svp_dim,log(1.*svp_dim/d)/2.+log(q), rhs  +log(svp_dim)/2.)
                    params.append([bkz_block_size, svp_dim, m])

    return params


def find_min_complexity(params):
    """
    For each valid and solving triple (bkz_dim, svp_dim, d) determines an
    approximate (!) cost and minimises.

    :param params: a list of all solving (bkz_dim, svp_dim, d) triples

    """
    min_cost = None
    min_cost_param = None
    expo = .349

    for param in params:

        bkz_block_size = param[0] - default_dim4free_fun(param[0])
        svp_dim = param[1] - default_dim4free_fun(param[1])
        d = param[2]

        bkz_cost = 2 * d * (2 ** (expo * bkz_block_size))
        finisher_svp_cost = 2 ** ((expo * svp_dim))
        new_cost = bkz_cost + finisher_svp_cost

        if min_cost is None or new_cost < min_cost:
            min_cost = new_cost
            min_cost_param = param

    return min_cost_param


# def sim_params(n, alpha):
#     A, c, q = load_lwe_challenge(n, alpha)
#     stddev = alpha*q
#     winning_params = []
#     for m in range(60, min(2*n+1, A.nrows+1)):
#         B = primal_lattice_basis(A, c, q, m=m)
#         M = GSO.Mat(B)
#         M.update_gso()
#         beta_bound = min(m+1, 110+default_dim4free_fun(110)+1)
#         svp_bound = min(m+1, 151)
#         rs = [M.get_r(i, i) for i in range(M.B.nrows)]
#         for beta in range(40, beta_bound):
#             rs, _ = simulate(rs, fplll_bkz.EasyParam(beta, max_loops=1))
#             for svp_dim in range(40, svp_bound):
#                 gh = gaussian_heuristic(rs[M.B.nrows-svp_dim:])
#                 if svp_dim*(stddev**2) < gh:
#                     winning_params.append([beta, svp_dim, m+1])
#                     break
#     min_param = find_min_complexity(winning_params)
#     return min_param


def primal_lattice_basis(A,  q, d=None):
    """
    Construct lattice basis for lattice challenge
    ``A`` defined modulo ``q``.

    :param A: lattice matrix : [[I A] 
                                [0 qI]]
    :param q: integer modulus, is also the value n = dim(qI)
    :param d: number of dimension to use
    
    return B = [[I A1] 
                [0 qI]], A1 is the first (d-n) rows of A

    """
    n = q
    m = d -n  #m is number of samples, i.e. rows of A.
    # full_m = A.nrows - n #full_n

    B = IntegerMatrix(d, d) 
    for i in range(m): 
        B[i,i] = 1
        for j in range(n):
            B[i, m+j] = A[i, -n+j]
        if(i<n):
            B[i+m, i+m] = q

    B = LLL.reduction(B)

    return B



def lattice_basis_randomly(A,  q, d=None, randomize =True):
    """
    Construct lattice basis for lattice challenge
    ``A`` defined modulo ``q``.

    :param A: lattice matrix : [[I A] 
                                [0 qI]]
    :param q: integer modulus, is also the value n = dim(qI)
    :param d: number of dimension to use
    :param randomize: randomize the lattice basis to eliminate q-vectors.
    
    return B = [[I A1] 
                [0 qI]], A1 is the first (d-n) rows of A
        

    """
    n = q
    m = d -n  #m is number of samples, i.e. rows of A.
    # full_m = A.nrows - n #full_n

    B = IntegerMatrix(d, d) 
    for i in range(m): 
        B[i,i] = 1
        for j in range(n):
            B[i, m+j] = A[i, -n+j]
        if(i<n):
            B[i+m, i+m] = q
            
    
    

    # random_matrix(ZZ,4,4, algorithm = 'unimodular')
    
    # print(IntegerMatrix.random(10, "qary", k=0, q=1))
    
    
    if(randomize):
        # print(q in B)
        num_q = q
        while(num_q > 0):
            #BKZ random
            M = GSO.Mat(B, float_type="double", flags=GSO.ROW_EXPO)
            bkz = BKZReduction(M)
            bkz.randomize_block(0, B.nrows, density=B.ncols//4)
            LLL.reduction(B)
            bkz = BKZReduction(B)
            
            #Left multiply a matrix with determinant = 1.
            P = IntegerMatrix.identity(B.ncols)
            for i in range(n):
                for j in range(n-i-1):
                    P[i,j] = randint(-1,1)
            B = P*B
            
            M = GSO.Mat(B, float_type="double", flags=GSO.ROW_EXPO)
            num_q = sum([1 for i in range(B.ncols) if M.get_r(i,i) == q**2])

    B = LLL.reduction(B)
    

    return B






def primal_lattice_basis_randomly(A, c, q, m=None, randomize = True):
    """
    Construct primal lattice basis for LWE challenge (primal attack)
    ``(A,c)`` defined modulo ``q``.

    :param A: LWE matrix, in dimension m*n
    :param c: LWE vector, in dimension m
    :param q: integer modulus
    :param m: number of samples to use (``None`` means all)

    :output param B: SVP matrix, in dimension m+n+1

    """
    if m is None:
        m = A.nrows
    elif m > A.nrows:
        raise ValueError("Only m=%d samples available." % A.nrows)
    n = A.ncols

    B = IntegerMatrix(m+n+1, m+1) 
    indices = []
    for i in range(m+1):
        index = randint(0,A.nrows-1)
        while(index in indices):
            index = randint(0,A.nrows-1)
        indices.append(index)
        
    
    for i in range(m):
        for j in range(n):
            B[j, i] = A[indices[i], j]
        B[i+n, i] = q
        B[-1, i] = c[indices[i]]
    B[-1, -1] = 1

    B = LLL.reduction(B)
    assert(B[:n] == IntegerMatrix(n, m+1))
    B = B[n:]
    
    
    

    return B




