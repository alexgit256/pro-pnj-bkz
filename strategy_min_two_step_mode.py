from strategy_gen.strategy_gen import lwechal_simulation_gsa, lwechal_simulation_actual_l
from g6k.utils.util import load_lwe_instance,load_lwe_challenge
from g6k.utils.lwe_estimation import gsa_params, primal_lattice_basis
from g6k.siever import Siever
from math import log, log2
from fpylll.tools.quality import basis_quality
from strategy_simulation import strategy_simulation

def find_min_strategy_for_given_strategy(n,alpha,S,float_type = "dd", load_lwe = "lwe_challenge"):
    Tmin = None
    Smin = None
    for i in range(len(S)):
        Si = S[:i+1]
        T = strategy_simulation(n,alpha,Si,load_lwe=load_lwe, simulation="actual_l",float_type = float_type)
        if(Tmin is None or T < Tmin):
            Tmin = T
            Smin = Si
        else:
            return Smin