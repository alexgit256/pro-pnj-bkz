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
from math import log,sqrt

from fpylll import BKZ as fplll_bkz
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll.tools.quality import basis_quality
from fpylll.util import gaussian_heuristic as gh

from g6k.algorithms.bkz import pump_n_jump_bkz_tour
from g6k.algorithms.our_pump import pump
# from g6k.algorithms.pump_cpu import pump
from g6k.siever import Siever
from g6k.utils.cli import parse_args, run_all, pop_prefixed_params
from g6k.utils.stats import SieveTreeTracer, dummy_tracer
from g6k.utils.util import load_lwe_challenge,load_lwe_challenge_mid

# from g6k.utils.lwe_estimation import gsa_params, primal_lattice_basis
from g6k.utils.lwe_estimation import gsa_params, primal_lattice_basis
from pump_estimation import pro_sieve_estimation_20230609
# from six.moves import range

#from pro_pnj_bkz_optimization import *


def lwe_kernel(arg0, params=None, seed=None):
    """
    Run the primal attack against Darmstadt LWE instance (n, alpha).

    :param n: the dimension of the LWE-challenge secret
    :param params: parameters for LWE:

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

    # params for underlying BKZ
    extra_dim4free = params.pop("bkz/extra_dim4free")
    jump = params.pop("bkz/jump")
    dim4free_fun = params.pop("bkz/dim4free_fun")
    
    
    pump_params = pop_prefixed_params("pump", params)
    beta_pump = pump_params.pop("dsvp")
    # print(beta_pump)
    fpylll_crossover = params.pop("bkz/fpylll_crossover")
    
    tours = params.pop("bkz/tours")

    # flow of the lwe solver
    svp_bkz_time_factor = params.pop("lwe/svp_bkz_time_factor")
    goal_margin = params.pop("lwe/goal_margin")
    blocksizes = params.pop("bkz/blocksizes")
    # generation of lwe instance and Kannan's embedding
    alpha = params.pop("lwe/alpha")
    m = params.pop("lwe/m")
    decouple = svp_bkz_time_factor > 0

    # misc
    dont_trace = params.pop("dummy_tracer")
    verbose = params.pop("verbose")

    A, c, q = load_lwe_challenge(n=n, alpha=alpha)
    
    print("-------------------------")
    print("Primal attack, LWE challenge n=%d, alpha=%.4f" % (n, alpha))

    if m is None:
        try:
            min_cost_param = gsa_params(n=A.ncols, alpha=alpha, q=q,
                                        decouple=decouple)
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

    # no use in having a very small b
    b = max(b, s-65)

    target_norm = goal_margin * (alpha*q)**2 * m + 1
    # target_norm = max( target_norm, 0.98 * full_gh)

    
    # B_=load_lwe_challenge_mid(n=n, alpha=alpha)
    # if B_ is not None:
    #     B = B_
    # else: 
    #     B = primal_lattice_basis(A, c, q, m=m)
    B = primal_lattice_basis(A, c, q, m=m) #debug

    g6k = Siever(B, params)
    print("GSO precision: ", g6k.M.float_type)
    print("||b_1|| = %d, target_norm = %d"  %(g6k.M.get_r(0, 0), target_norm))

    if dont_trace:
        tracer = dummy_tracer
    else:
        tracer = SieveTreeTracer(g6k, root_label=("lwe"), start_clocks=True)

    d = g6k.full_n

    g6k.lll(0, g6k.full_n)
    slope = basis_quality(g6k.M)["/"]
    sigma = alpha * q
    log_rr = [log(g6k.M.get_r(i, i))/2 - log(sigma) for i in range(d)]
    dvol = sum(log_rr)
    print("Intial Slope = %.5f, dim = %d, dvol = %3.13f\n" %(slope, d, dvol))

    T0 = time.time()
    T0_BKZ = time.time()

    
    if blocksizes is None:
        # blocksizes = list(range(10, d)) + list(reversed(range(b-14, 60, -10))) + list(range(b - 12, b + 25, 2)) # noqa
        blocksizes = []
    else:
        if(blocksizes == "[True]"):
            blocksizes = []
        else:
            blocksizes = blocksizes.replace("[(","")
            blocksizes = blocksizes.replace(")]","")
            blocksizes = blocksizes.split("), (")
            
            blocksizes = [_.split(", ") for _ in blocksizes]
            blocksizes = [(int(_[0]), int(_[1]), int(_[2])) for _ in blocksizes]
    print("Blocksize Strategy: ", end= "")    
    print(blocksizes)
    print()
    
    
    #(130,  2, 3),
    # blocksizes = [(133,  2,  1),(134,  2,  2),(136,  2,  1),(138,  2,  1),(139,  2,  1),(141,  2,  2),(144,  2,  2),(145,  2,  1),(146,  2,  1),(148,  2,  1),(149,  2,  1),(150,  2,  1),(151, 15, 10),(152, 15,  2),(152,  2,  1),(153, 15, 10),(153, 14, 10),(153, 13, 10),(153, 12, 10),(154, 15, 10),(154, 14, 10),(154, 13, 10),(154, 12, 10),(154, 11,  9),(155, 15, 10),(155, 14, 10),(155, 13, 10),(155, 12, 10),(155, 11,  7),(156, 15, 10),(156, 14, 10),(156, 13,  8),(156,  4,  1),(157, 15, 10),(157, 14, 10),(157, 13, 10),(157, 12, 10),(157, 11, 10),(157, 10,  1),(158, 15, 10),(158, 14, 10),(158, 13, 10),(158, 12, 10),(158, 11, 10),(158, 10, 10),(158,  4,  1),(159, 15, 10),(159, 14, 10),(159, 13,  9),(159, 12,  8),(159, 11,  4),(160, 15,  9),(160, 14, 10),(160, 13,  9),(160, 12,  8),(160, 11,  3),(161, 14,  9)] #(blocksize, jump, tours) for 95-005
    # blocksizes = [(144,  4,  1),(147,  4,  1),(153,  4,  1)]

    # blocksizes = [(90,10,1)]

    # blocksizes = []
    # blocksize = 1
    

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
                if blocksize <= 65:
                    max_RAM = pump_n_jump_bkz_tour(g6k, tracer, blocksize, jump=1,
                                     verbose=verbose,
                                     extra_dim4free=extra_dim4free,
                                     dim4free_fun=dim4free_fun,
                                     goal_r0=target_norm,
                                     pump_params=pump_params)
                else:
                    max_RAM = pump_n_jump_bkz_tour(g6k, tracer, blocksize, jump=jump,
                                     verbose=verbose,
                                     extra_dim4free=extra_dim4free,
                                     dim4free_fun=dim4free_fun,
                                     goal_r0=target_norm,
                                     pump_params=pump_params)
                    
                    
            g6k.lll(0, g6k.full_n)
            
            #write the mid result of basis
            # alpha_ = int(alpha*1000)
            # filename = 'lwechallenge/%03d-%03d-midmat.txt' % (n, alpha_)
            # fn = open(filename, "w")
            # fn.write(str(n)+'\n')
            # fn.write(str(m)+'\n')
            # fn.write(str(q)+'\n')
            # fn.write(str(alpha)+'\n')
            # fn.write('[')
            # for i in range(g6k.M.B.nrows):
            #     fn.write('[')
            #     for j in range(g6k.M.B.ncols):
            #         fn.write(str(g6k.M.B[i][j]))
            #         if j<g6k.M.B.ncols-1:
            #             fn.write(' ')
            #     if i < g6k.M.B.nrows-1:
            #         fn.write(']\n')
            # fn.write(']]')
            # fn.close()


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

            if g6k.M.get_r(0, 0) <= target_norm or g6k.M.B[0][-1] == 1 or g6k.M.B[0][-1] == -1:
                break
            
    if not(g6k.M.get_r(0, 0) <= target_norm or g6k.M.B[0][-1] == 1 or g6k.M.B[0][-1] == -1):
        
     
        # pump_time,llb,beta_pump,f = pro_sieve_estimation_20230609(log_rr,q, alpha)
                
        n_max= 135
        
        llb = d - beta_pump
        f = max(0, beta_pump - n_max)
        T0_pump = time.time()
        print("Without otf, would expect solution at pump_{%d, %d, %d},n_max = %d" % (llb, beta_pump , f, n_max)) # noqa
                
        # if(beta_pump - f > n_max):
        #     # beta_pump  = n_max + f
        #     # llb = d - beta_pump
        #     f = beta_pump - n_max
            
        # if(beta_pump - f <= n_max):
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

                    

        # if g6k.M.get_r(0, 0) <= target_norm:
        #     break
                
        g6k.lll(0, g6k.full_n)
                
                
            # if g6k.M.get_r(0, 0) <= target_norm:
            #     break
        
        
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


    if g6k.M.get_r(0, 0) <= target_norm or g6k.M.B[0][-1] == 1 or g6k.M.B[0][-1] == -1:
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
