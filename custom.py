#!/usr/bin/env python
# -*- coding: utf-8 -*-
####
#
#   Copyright (C) 2018-2021 Team G6K
#
#   This file is part of G6K. G6K is free software:
#   you can redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free Software Foundation,
#   either version 2 of the License, or (at your option) any later version.
#
#   G6K is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with G6K. If not, see <http://www.gnu.org/licenses/>.
#
####


"""
LWE Challenge Solving Command Line Client
"""

from __future__ import absolute_import
from __future__ import print_function
import copy
import re
import sys
import time

from collections import OrderedDict # noqa
from math import log,sqrt, log2, floor

from fpylll import BKZ as fplll_bkz
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll.tools.quality import basis_quality

# from g6k.algorithms.bkz import pump_n_jump_bkz_tour
from g6k.algorithms.bkz_ds import pump_n_jump_bkz_tour
from g6k.algorithms.pump import pump
# from g6k.algorithms.pump_cpu import pump
from g6k.siever import Siever
from g6k.utils.cli import parse_args, run_all, pop_prefixed_params
from g6k.utils.stats import SieveTreeTracer, dummy_tracer
from g6k.utils.util import load_lwe_instance, load_lwe_challenge

# from g6k.utils.lwe_estimation import gsa_params, primal_lattice_basis
from g6k.utils.lwe_estimation import gsa_params, primal_lattice_basis
from pump_estimation import pump_estimation
from strategy_gen.strategy_gen import EnumBS, BSSA
from numpy import float64
from fpylll.util import gaussian_heuristic
from math import log, log2
from fpylll.tools.quality import basis_quality


import pickle
from sample import *
from utills import *
from lwe_gen import *
from lwe_gen import module
#- - -
import copy
import re
import sys
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import os


from collections import OrderedDict # noqa
from math import pi,exp,log,sqrt,lgamma
from PumpDimEst_comparison import expected_value_estimate, chi_square_estimate
# - - -

def pnjBKZ_simulator(log_rr0,beta,N,d,jump):
    l = []
    for i in range(d):
        temp = log_rr0[i]
        l.append(temp)
    #print(len(l))
    l_ = []
    J = jump
    randomSquaredAverages = [2.95747208 , 2.905419231 , 2.808209731 , 2.704122291 , 2.589140986 , 2.473617892 , 2.363752978 , 2.254288677 , 2.160395606 , 2.056417068 , 1.962571394 , 1.86329581 , 1.781471788 , 1.691206302 , 1.607855519 , 1.526258286 , 1.45048576 , 1.377169955 , 1.304800173 , 1.238714637 , 1.172164783 , 1.11055388 , 1.04872671 , 0.9933346386 , 0.9385826564 , 0.8858378414 , 0.8346947761 , 0.7869433841 , 0.743196743 , 0.6999110693 , 0.6612589966 , 0.620890347 , 0.5840212199 , 0.5494461008 , 0.5153120689 , 0.4851862344 , 0.4542255962 , 0.426615261 , 0.4011004324 , 0.3761683243 , 0.3521434119 , 0.3305054658 , 0.3109962405 , 0.2976205498 , 0.2897254705]
    #print(len(randomSquaredAverages))
    rk = []
    for i in range(len(randomSquaredAverages)):
        RK = log(math.sqrt(randomSquaredAverages[i]))
        rk.append(RK)
    #print(rk)
    cd = []
    for i in range(beta):
        CD = lgamma(((i+1)/2.0 + 1))*(1/(i+1))-log(pi)/2
        cd.append(CD)
    #print(cd)
    print(N)
    for tours in range(N):
        flag = True
        for k in range(d - beta):
            beta_ = min(beta, d - k)
            if k % J == 0:
                f = min(k + beta , d)
                #之前的 f = min(k + beta, d)
                sumf = 0
                sumk = 0
                for i in range(f):
                    sumf = sumf + l[i]
                for i in range(k):
                    sumk = sumk + l_[i]
                logV = sumf - sumk
                if flag == True:
                    if logV / beta_ + cd[beta_-1] < l[k]:
                        l_k = logV / beta_ + cd[beta_-1]
                        if tours == 0:
                            l_.append(l_k)
                        else:
                            l_[k] = l_k
                        flag = False
                    else:
                        l_k = l[k]
                        if tours == 0:
                            l_.append(l_k)
                        else:
                            l_[k] = l_k
                else:
                    l_k = logV / beta_ + cd[beta_-1]
                    if tours == 0:
                        l_.append(l_k)
                    else:
                        l_[k] = l_k
            else:
                f = min(k - (k % J) + beta, d)
                sumf = 0
                sumk = 0
                for i in range(f):
                    sumf = sumf + l[i]
                for i in range(k):
                    sumk = sumk + l_[i]
                logV = sumf - sumk
                if flag == True:
                    if logV / (beta_-(k % J)) + cd[(beta_-(k % J))-1] < l[k]:
                        l_k = logV / (beta_-(k % J)) + cd[(beta_-(k % J))-1]
                        if tours == 0:
                            l_.append(l_k)
                        else:
                            l_[k] = l_k
                            flag = False
                    else:
                        l_k = l[k]
                        if tours == 0:
                            l_.append(l_k)
                        else:
                            l_[k] = l_k
                else:

                    l_k = logV / (beta_-(k % J)) + cd[(beta_-(k % J))-1]
                    if tours == 0:
                        l_.append(l_k)
                    else:
                        l_[k] = l_k
        for k in range(d - beta,d - 45):
            beta_ = d - k
            f = d
            sumf = 0
            sumk = 0
            for i in range(f):
                sumf = sumf + l[i]
            for i in range(k):
                sumk = sumk + l_[i]
            logV = sumf - sumk
            if flag == True:
                if logV / beta_ + cd[beta_-1] < l[k]:
                    l_k = logV / beta_ + cd[beta_-1]
                    if tours == 0:
                        l_.append(l_k)
                    else:
                        l_[k] = l_k
                    flag = False
                else:
                    l_k = l[k]
                    if tours == 0:
                        l_.append(l_k)
                    else:
                        l_[k] = l_k
            else:
                l_k = logV / beta_ + cd[beta_-1]
                if tours == 0:
                    l_.append(l_k)
                else:
                    l_[k] = l_k

            #print(l_)
        k_ = min (len(randomSquaredAverages), beta)
        #last 45 norms
        sumf=0;
        sumk=0;
        for i in range(d):
            sumf = sumf + l[i]
        for i in range(d - 45):
            sumk = sumk + l_[i]
        logV = sumf - sumk
        for k in range(d - k_, d):
            l_k = logV/k_ + rk[k + 45 - d]
            if tours == 0:
                l_.append(l_k)
            else:
                l_[k] = l_k
                #Set l[i] as l_[i]
        for i in range(d):
            l[i] = l_[i]
    return l_

def kyberGen(n, q = 3329, eta = 3, k=1):
    polys = []
    for i in range(k*k):
        polys.append( uniform_vec(n,0,q) )
    A = module(polys, k, k)

    return A,q

def se_gen(k,n,eta):
    s = binomial_vec(k*n, eta)
    e = binomial_vec(k*n, eta)
    return s, e

def generateLWEInstances(n, q = 3329, eta = 3, k=1, ntar=5):
    A,q = kyberGen(n,q = q, eta = eta, k=k)
    bse = []
    for _ in range(ntar):
        s, e = se_gen(k,n,eta)
        b = (s.dot(A) + e) % q
        bse.append( (b,s,e) )

    return A,q,bse

def primal_lattice_basis_rows(A, c, q, m=None):
    """
    Construct primal lattice basis for LWE challenge
    ``(A,c)`` defined modulo ``q``.

    :param A: LWE matrix
    :param c: LWE vector
    :param q: integer modulus
    :param m: number of samples to use (``None`` means all)

    """
    if m is None:
        m = A.nrows
    elif m > A.nrows:
        raise ValueError("Only m=%d samples available." % A.nrows)
    n = A.ncols

    B = IntegerMatrix(m+n+1, m+1)
    for i in range(m):
        for j in range(n):
            B[i, j] = A[i, j]
        B[i+n, i] = q
        B[-1, i] = c[i]
    B[-1, -1] = 1

    B = LLL.reduction(B)
    assert(B[:n] == IntegerMatrix(n, m+1))
    B = B[n:]

    return B

def lwe_kernel(arg0, params=None, seed=None):
    """
    Run the primal attack against Darmstadt LWE instance (n, alpha).

    :param n: the dimension of the LWE-challenge secret
    :param params: parameters for LWE:
        - kyber/n: the n parameter of kyber

        - kyber/q: modulus

        - kyber/k: algebraic dimension of kyber

        - kyber/eta: parameter of kyber's binom. dist.

        - lwe/alpha: the noise rate of the LWE-challenge

        - lwe/m: the number of samples to use for the primal attack

        - lwe/goal_margin: accept anything that is
          goal_margin * estimate(length of embedded vector)
          as an lwe solution

        - lwe/svp_bkz_time_factor: if > 0, run a larger pump when
          svp_bkz_time_factor * time(BKZ tours so far) is expected
          to be enough time to find a solution

        - bkz/blocksizes: given as low:high:inc perform BKZ reduction
          with blocksizes in range(low, high, inc) (after some light)
          prereduction

        - bkz/tours: the number of tours to do for each blocksize

        - bkz/jump: the number of blocks to jump in a BKZ tour after
          each pump

        - bkz/extra_dim4free: lift to indices extra_dim4free earlier in
          the lattice than the currently sieved block

        - bkz/fpylll_crossover: use enumeration based BKZ from fpylll
          below this blocksize

        - bkz/dim4free_fun: in blocksize x, try f(x) dimensions for free,
          give as 'lambda x: f(x)', e.g. 'lambda x: 11.5 + 0.075*x'

        - pump/down_sieve: sieve after each insert in the pump-down
          phase of the pump

        - dummy_tracer: use a dummy tracer which captures less information

        - verbose: print information throughout the lwe challenge attempt

    """

    # Pool.map only supports a single parameter
    if params is None and seed is None:
        n, params, seed = arg0
    else:
        n = arg0

    params = copy.copy(params)
    # n = params.pop("kyber/n")
    q = params.pop("kyber/q")
    k = params.pop("kyber/k")
    eta = params.pop("kyber/eta")
    D = centeredBinomial( eta )
    # D.secondMoment**0.5 = alpha * q
    alpha = D.secondMoment**0.5 / q

    print(f"n,q,k,eta: {n,q,k,eta}", flush=True)
    # n = 190
    # q = 3329
    # k = 1
    # eta = 3

    # params for underlying BKZ
    extra_dim4free = params.pop("bkz/extra_dim4free")
    jump = params.pop("bkz/jump")
    dim4free_fun = params.pop("bkz/dim4free_fun")


    pump_params = pop_prefixed_params("pump", params)
    if "dsvp" in pump_params:
        beta_pump = pump_params.pop("dsvp")
    else:
        beta_pump = None
    if "succ_prob" in pump_params:
        succ_prob = pump_params.pop("succ_prob")
    # else:
    #     succ_prob = None
    # print(beta_pump)
    fpylll_crossover = params.pop("bkz/fpylll_crossover")

    tours = params.pop("bkz/tours")

    # flow of the lwe solver
    svp_bkz_time_factor = params.pop("lwe/svp_bkz_time_factor")
    goal_margin = params.pop("lwe/goal_margin")
    blocksizes = params.pop("bkz/blocksizes")
    # generation of lwe instance and Kannan's embedding
    # alpha = params.pop("lwe/alpha")
    m = params.pop("lwe/m")
    decouple = svp_bkz_time_factor > 0

    # misc
    dont_trace = params.pop("dummy_tracer")
    verbose = params.pop("verbose")
    strategy_method = params.pop("strategy_method")
    load_lwe = params.pop("load_lwe")
    float_type = params.pop("float_type")
    max_jump = params.pop("max_jump")
    if(max_jump is None):
        max_jump = 100
    set_j1 = params.pop("set_j1")
    gen_strategy_only = params.pop("gen_strategy_only")
    max_RAM = params.pop("max_RAM")
    if(max_RAM is None):
        max_RAM = 1000

    print("-------------------------")
    # if(load_lwe == "lwe_instance"):
    #     A, c, q = load_lwe_instance(n=n, alpha=alpha)
    #     print("Primal attack, LWE instance n=%d, alpha=%.4f" % (n, alpha))
    # if(load_lwe == "lwe_challenge" or load_lwe is None):
    #     A, c, q = load_lwe_challenge(n=n, alpha=alpha)
    #     print("Primal attack, LWE challenge n=%d, alpha=%.4f" % (n, alpha))
    Anumpy, q, bse =  generateLWEInstances(n, q, eta, k, ntar=1)
    # print(f"Anumpy: {Anumpy.shape}")
    A = IntegerMatrix.from_matrix( [ [ int(Anumpy[i,j]) for j in range(len(Anumpy[0])) ] for i in range(len(Anumpy)) ] )
    bvec = bse[0][0]
    c = bvec
    print("Primal attack,Kyber n=%d, eta=%.4f" % (n, eta))


    m = n
    """
    if m is None:
        try:
            min_cost_param = gsa_params(n=A.ncols, alpha=alpha, q=q,
                                        decouple=decouple, samples = A.nrows)
            (b, s, m) = min_cost_param
        except TypeError:
            raise TypeError("No winning parameters.")
    else:
        try:
            min_cost_param = gsa_params(n=A.ncols, alpha=alpha, q=q,
                                        decouple=decouple)
            (b, s, _) = min_cost_param
        except TypeError:
            raise TypeError("No winning parameters.")
    print("Chose %d samples. Predict solution at bkz-%d + svp-%d" % (m, b, s))
    print()
    """


    # no use in having a very small b
    b = 65 #max(b, s-65)

    evec, svec = bse[0][1:]
    esvec = np.concatenate([evec,-svec])
    esnorm = float(esvec@esvec)
    target_norm =  esnorm #goal_margin * (alpha*q)**2 * m + 1
    # target_norm = max( target_norm, 0.98 * full_gh)


    # B_=load_lwe_challenge_mid(n=n, alpha=alpha)
    # if B_ is not None:
    #     B = B_
    # else:
    #     B = primal_lattice_basis(A, c, q, m=m)
    # B = primal_lattice_basis_rows(A, [int(cc) for cc in c], int(q), m=m) #debug
    nrow, ncol = Anumpy.shape
    t = np.concatenate([bvec,[0]*nrow]) #BDD target
    B = [ [int(0) for i in range(2*k*n+1)] for j in range(2*k*n+1) ]
    for i in range( k*n ):
        B[i][i] = int( q )
    for i in range(k*n, 2*k*n+1):
        B[i][i] = 1
    for i in range(k*n, 2*k*n):
        for j in range(k*n):
            B[i][j] = int( A[i-k*n,j] )

    for j in range(k*n):
        B[-1][j] = int( t[j] )
    B = IntegerMatrix.from_matrix( B )


    g6k = Siever(B, params, float_type = float_type)
    print("GSO precision: ", g6k.M.float_type)
    print("||b_1|| = %d, target_norm = %d"  %(g6k.M.get_r(0, 0), target_norm))

    if dont_trace:
        tracer = dummy_tracer
    else:
        tracer = SieveTreeTracer(g6k, root_label=("lwe"), start_clocks=True)

    d = g6k.full_n

    g6k.lll(0, g6k.full_n)
    g6k.update_gso(0,d)
    slope = basis_quality(g6k.M)["/"]
    # D = centeredBinomial( 3 )
    sigma =  D.secondMoment**0.5 #alpha * q
    print(f"sigma: {sigma} alpha: {alpha}")
    dvol = g6k.M.get_log_det(0,d)/2. - log(sigma)*d
    print("Intial Slope = %.5f, dim = %d, dvol = %3.13f\n" %(slope, d, dvol))


    log2_rr = [round((log2(g6k.M.get_r(i,i))/2.) - (log2(sigma)),15) for i in range(d)]

    if(strategy_method == "enumbs"):
        enumbs = EnumBS(d,g6k.M.float_type,max_jump=max_jump, max_RAM = max_RAM)
        T0_enumbs = time.time()
        enumbs(log2_rr)
        # enumbs(d,dvol)
        sys.stdout.flush()
        print("Cost for generate strategy through EnumBS: %.2f sec" %(time.time()-T0_enumbs))
        blocksizes = enumbs.get_strategy()
        target_slope = enumbs.get_target_slope()

    if(strategy_method == "bssav1"):
        bssa = BSSA(d,"v1",g6k.M.float_type,max_jump=max_jump, max_RAM = max_RAM)
        T0_bssa = time.time()
        bssa(log2_rr)
        sys.stdout.flush()
        print("Cost for generate strategy through BSSAv1: %.2f sec" %(time.time()-T0_bssa))
        blocksizes =bssa.get_strategy()

    if(strategy_method == "bssav2"):
        bssa = BSSA(d,"v2",g6k.M.float_type,max_jump=max_jump, max_RAM = max_RAM)
        T0_bssa = time.time()
        bssa(log2_rr)
        sys.stdout.flush()
        print("Cost for generate strategy through BSSAv2: %.2f sec" %(time.time()-T0_bssa))
        blocksizes =bssa.get_strategy()

    if(strategy_method is None or blocksizes is None) :
        blocksizes = list(range(10, d)) + list(reversed(range(b-14, 60, -10))) + list(range(b - 12, b + 25, 2)) # noqa
        blocksizes = [(_,1,1) for _ in blocksizes[:10]]
        # blocksizes = []
    log_rr0 = [ log(tmp) for tmp in g6k.M.r() ]
    # log_rr0 = pnjBKZ_simulator(log_rr0,50,10,d,1)
    for S in blocksizes[:-1]:
        (blocksize, jump, tours) = S
        log_rr0 = pnjBKZ_simulator(log_rr0,blocksize,tours,d,jump)
    # beta_pump = min(d, pump_estimation(log_rr0,q, alpha)[1] + 1)
    rr = [exp(tmp) for tmp in log_rr0]
    pump_est = pump_estimation(rr,q, alpha)
    print( f"pump_est: {pump_est}" )
    betaest, betachi = expected_value_estimate(rr,sigma), chi_square_estimate(rr,sigma)
    print(f"betaest, betachi: {betaest, betachi}")

    if(set_j1 == 1):
        blocksizes = [(blocksize, 1, tours) for (blocksize, _, tours) in blocksizes]

    print("Blocksize Strategy: ", end= "")
    print(blocksizes)
    print()


    T0 = time.time()
    T0_BKZ = time.time()

    # print(abs(basis_quality(g6k.M)["/"] - target_slope),basis_quality(g6k.M)["/"],target_slope)
    # while( abs(basis_quality(g6k.M)["/"] - target_slope)> 0.001):
    if(gen_strategy_only is None or gen_strategy_only != 1):
        for S in blocksizes:
            (blocksize, jump, tours) = S
            for tt in range(tours):
                # BKZ tours

                if blocksize < fpylll_crossover:
                    print("Starting a fpylll BKZ-%d tour. " % (blocksize), end=' ')
                    sys.stdout.flush()
                    # if verbose:
                    #     print("Starting a fpylll BKZ-%d tour. " % (blocksize), end=' ')
                    #     sys.stdout.flush()
                    bkz = BKZReduction(g6k.M)
                    par = fplll_bkz.Param(blocksize,
                                        strategies=fplll_bkz.DEFAULT_STRATEGY,
                                        max_loops=1)
                    bkz(par)

                else:
                    print("Starting a pnjBKZ-%d-%d tour. " % (blocksize,jump))
                    sys.stdout.flush()
                    # if verbose:
                    #     print("Starting a pnjBKZ-%d tour. " % (blocksize))
                    max_RAM = pump_n_jump_bkz_tour(g6k, tracer, blocksize, jump=jump,
                                        verbose=verbose,
                                        extra_dim4free=extra_dim4free,
                                        dim4free_fun=dim4free_fun,
                                        goal_r0=target_norm,
                                        pump_params=pump_params)


                g6k.lll(0, g6k.full_n)

                #write the mid result of basis
                alpha_ = int(alpha*1000)
                filename = 'lwechallenge/%03d-%03d-midmat.txt' % (n, alpha_)
                fn = open(filename, "w")
                fn.write(str(n)+'\n')
                fn.write(str(m)+'\n')
                fn.write(str(q)+'\n')
                fn.write(str(alpha)+'\n')
                fn.write('[')
                for i in range(g6k.M.B.nrows):
                    fn.write('[')
                    for j in range(g6k.M.B.ncols):
                        fn.write(str(g6k.M.B[i][j]))
                        if j<g6k.M.B.ncols-1:
                            fn.write(' ')
                    if i < g6k.M.B.nrows-1:
                        fn.write(']\n')
                fn.write(']]')
                fn.close()


                T_BKZ = time.time() - T0_BKZ

                slope = basis_quality(g6k.M)["/"]
                fmt = "slope: %.5f,||b_1|| = %d, target_norm = %d, BKZ cost: %.3f s, walltime: %.3f sec"
                if(blocksize < fpylll_crossover):
                    print(fmt % (slope, g6k.M.get_r(0, 0), target_norm, T_BKZ, time.time() - T0))
                else:
                    fmt += ", memory cost = %3.2f GB "
                    print(fmt % (slope, g6k.M.get_r(0, 0), target_norm, T_BKZ, time.time() - T0, max_RAM))
                sys.stdout.flush()


                T0_BKZ = time.time()

                if g6k.M.get_r(0, 0) <= target_norm: #or g6k.M.B[0][-1] == 1 or g6k.M.B[0][-1] == -1:
                    print("Finished! TT=%.2f sec" % (time.time() - T0))
                    print(g6k.M.B[0])
                    alpha_ = int(alpha*1000)
                    filename = 'lwechallenge/%03d-%03d-solution.txt' % (n, alpha_)
                    fn = open(filename, "w")
                    fn.write(str(g6k.M.B[0]))
                    fn.close()
                    return

        if not (g6k.M.get_r(0, 0) <= target_norm ):#or g6k.M.B[0][-1] == 1 or g6k.M.B[0][-1] == -1):
            if(beta_pump is None):
                rr = [g6k.M.get_r(i,i) for i in range(d)]
                # if(succ_prob is not None):
                #     beta_pump = pump_estimation(rr,q, alpha, succ_prob = succ_prob)
                # else:
                beta_pump = min(d, pump_estimation(rr,q, alpha)[1] + 1)

            n_max= 143

            llb = d - beta_pump
            f = max(accs_2023_d4f(slope), beta_pump - n_max)

            T0_pump = time.time()
            print("Without otf, would expect solution at pump_{%d, %d, %d},n_max = %d" % (llb, beta_pump , f, n_max)) # noqa


            if verbose:
                print()
                print( "Starting svp pump_{%d, %d, %d}" % (llb, d-llb, f) ) # noqa
                sys.stdout.flush()


            _, max_RAM_cost = pump(g6k, tracer, llb, d-llb, f, verbose=verbose, goal_r0=target_norm * (d - llb)/(1.*d),**pump_params)


            if verbose:
                T_pump = time.time() - T0_pump
                slope = basis_quality(g6k.M)["/"]
                fmt = "slope: %.5f, T_pump = %.3f sec, RAM_pump = %.3f GB, walltime: %.3f sec"
                print(fmt % (slope,T_pump, max_RAM_cost, time.time()-T0))


            g6k.lll(0, g6k.full_n)



            #write the result of basis after last pump
            alpha_ = int(alpha*1000)
            filename = 'lwechallenge/%03d-%03d-last-pump.txt' % (n, alpha_)
            fn = open(filename, "w")
            fn.write(str(n)+'\n')
            fn.write(str(m)+'\n')
            fn.write(str(q)+'\n')
            fn.write(str(alpha)+'\n')
            fn.write('[')
            for i in range(g6k.M.B.nrows):
                fn.write('[')
                for j in range(g6k.M.B.ncols):
                    fn.write(str(g6k.M.B[i][j]))
                    if j<g6k.M.B.ncols-1:
                        fn.write(' ')
                if i < g6k.M.B.nrows-1:
                    fn.write(']\n')
            fn.write(']]')
            fn.close()


        if g6k.M.get_r(0, 0) <= target_norm: #or g6k.M.B[0][-1] == 1 or g6k.M.B[0][-1] == -1:
            print("Finished! TT=%.2f sec" % (time.time() - T0))
            print(g6k.M.B[0])
            alpha_ = int(alpha*1000)
            filename = 'lwechallenge/%03d-%03d-solution.txt' % (n, alpha_)
            fn = open(filename, "w")
            fn.write(str(g6k.M.B[0]))
            fn.close()
            return


        raise ValueError("No solution found.")

def lwe():
    """
    Attempt to solve an lwe challenge.

    """
    description = lwe.__doc__

    args, all_params = parse_args(description,
                                  lwe__alpha=0.005,
                                  lwe__m=None,
                                  lwe__goal_margin=1.5,
                                  lwe__svp_bkz_time_factor=1,
                                  bkz__blocksizes=None,
                                  bkz__tours=1,
                                  bkz__jump=1,
                                  bkz__extra_dim4free=12,
                                  bkz__fpylll_crossover=51,
                                  bkz__dim4free_fun="default_dim4free_fun",
                                  pump__down_sieve=True,
                                  dummy_tracer=True,  # set to control memory
                                  verbose=True
                                  )

    stats = run_all(lwe_kernel, list(all_params.values()), # noqa
                    lower_bound=args.lower_bound,
                    upper_bound=args.upper_bound,
                    step_size=args.step_size,
                    trials=args.trials,
                    workers=args.workers,
                    seed=args.seed)


if __name__ == '__main__':
    lwe()


# if __name__=="__main__":
#     n, q, eta, k = 144, 3329, 3, 1
#     decouple = True
#     samples = 2*n
#     d = None
#
#     ntar = 5
#     A, q, bse =  generateLWEInstances(n, q, eta, k, ntar)
#
#     stddev = 2.3333
#     for b, s, err in bse:
#         es = np.concatenate( [err,-s] )
#         stddev += (es@es)**0.5
#     stddev /= len(bse)
