#SPIKING NEURAL NETWORK NECESSITIES
from brian2 import *
#FOR PLOTTING AND CHECKING
import matplotlib.pyplot as plt
import math

#first, we're gonna start with the basics, setting up a single Leaky Integrate and Fire neuron

class boid_net():

    def __init__(self):
        start_scope()
        self.A = 2.5
        self.f = 10*Hz
        self.tau = 5*ms
        self.N = 5 #4 Neurons for input from 'sensors', 1 for output controlling direction

        # Create a TimedArray and set the equations to use it
        self.t_recorded = arange(int(200*ms/defaultclock.dt))*defaultclock.dt
        self.I_recorded = TimedArray(self.A*math.sin(2*math.pi*self.f*self.t_recorded), dt=defaultclock.dt)
        # TimedArray appears to take in as input an array of values then the time interval.
        # 

        self.eqs = '''
        dv/dt = (I-v)/self.tau : 1
        I = self.I_recorded(t) : 1
        '''

        self.G = NeuronGroup(self.N, self.eqs, threshold='v>1', reset='v=0', method='exact')
        self.M = StateMonitor(self.G, variables=True, record=True)
        self.S = Synapses(self.G, self.G, 'w : 1', on_pre='v_post += w')
        #current synapse weight is 1 for all synapses, this will be a problem

        self.S.connect(i=0, j=[1, 2, 3, 4])
    
    def run(self, dt):
        run(dt)

    def plot(self):
        plt.plot(self.M.t/ms, self.M.v[0], label='v')
        plt.plot(self.M.t/ms, self.M.I[0], label='I')
        plt.xlabel('Time (ms)')
        plt.ylabel('v')
        plt.legend(loc='best')
        plt.show()
