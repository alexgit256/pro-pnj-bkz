load("pnjbkz_simulator.sage")

from math import log


def draw_dim_chi_relation_fig():
    dim_ = 2049
    dvol = 15614.219
    #for dim_ in range(100,101,10):
    if(True):
        #print("Generate gs-lengths by GSA assumption.")
        delta = compute_delta(2)
        l = [log(bkzgsa_gso_len(dvol, i, dim_, delta=delta)) / log(2) for i in range(dim_)]
        remaining_proba = 1.
        cumulated_proba = 0.
        for beta in range(50, dim_):
            l = simulate_pnjBKZ(l, beta, 1, 1)#simulate_pnjBKZ(log_GS_lengths, beta, loop, jump)
            proba = chisquared_table[beta].cum_distribution_function(
                        2**(2 * l[dim_ - beta]))

            cumulated_proba += remaining_proba * proba
            remaining_proba = 1. - cumulated_proba 
            print(dim_, beta,  dvol, l[dim_ - beta], proba, cumulated_proba)


draw_dim_chi_relation_fig()