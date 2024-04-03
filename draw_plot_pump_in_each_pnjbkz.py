import matplotlib.pyplot as plt 
from scipy import optimize
import os
from random import randint
      
def draw_plot_pump_in_pnjbkz(indices,PumpCosts,filename):
    with plt.style.context(['seaborn-white',"science"]):
        fig, ax = plt.subplots(figsize=(5,3),dpi=600) 
        color_index = randint(256*256*128,256*256*256)
        color = "#"+(hex(color_index).replace('0x', '').zfill(6)) 
        print(len(indices),len(PumpCosts))
        ax.scatter([_[0] for _ in indices], PumpCosts, marker='_',color=color, s=10.)
        # plt.legend(loc = (0,1))#[scatter, function1,function2])
        font1 = {'family' : 'Times New Roman',
                'weight' : 'normal',
                'size'   : 6.5
            }
        # plt.legend(prop=font1,frameon = True)
        ax.set(xlabel=r'index of $(\kappa,\beta,f)$')
        ax.set(ylabel=r'$T_{\rm pump}$(s)')
        ax.autoscale(tight=False)
        fig.savefig(filename)  



