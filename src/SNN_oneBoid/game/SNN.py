#SPIKING NEURAL NETWORK NECESSITIES
from brian2 import *
#FOR PLOTTING AND CHECKING
import matplotlib.pyplot as plt

class boid_net():

    def __init__(self):
        start_scope()
        self.taupre = self.taupost = 20*ms
        self.Apre = 0.01
        self.Apost = -self.Apre*self.taupre/self.taupost*1.05
        self.tmax = 50*ms
        self.N = 4
        self.G = NeuronGroup(N, 'tspike:second', threshold='t>tspike', refractory=100*ms)
        self.H = NeuronGroup(N, 'tspike:second', threshold='t>tspike', refractory=100*ms)
        self.G.tspike = 'i*tmax/(N-1)'
        self.H.tspike = '(N-1-i)*tmax/(N-1)'
        # Presynaptic neurons G spike at times from 0 to tmax
        # Postsynaptic neurons G spike at times from tmax to 0
        # So difference in spike times will vary from -tmax to +tmax   

        self.S = Synapses(self.G, self.H,
                    '''
                    w : 1
                    dapre/dt = -apre/self.taupre : 1 (event-driven)
                    dapost/dt = -apost/self.taupost : 1 (event-driven)
                    ''',
                    on_pre='''
                    apre += self.Apre
                    w = w+apost
                    ''',
                    on_post='''
                    apost += self.Apost
                    w = w+apre
                    ''')
        self.S.connect(j='i')
    

    def run(self, dt):
        run(dt)

    def plot(self):
        plt.plot((self.H.tspike-self.G.tspike)/ms, S.w)
        plt.xlabel(r'$\Delta t$ (ms)')
        plt.ylabel(r'$\Delta w$')
        plt.axhline(0, ls='-', c='k')
        plt.show()
