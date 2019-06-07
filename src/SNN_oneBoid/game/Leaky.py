#SPIKING NEURAL NETWORK NECESSITIES
from brian2 import *
#FOR PLOTTING AND CHECKING
import matplotlib.pyplot as plt
import math

#first, we're gonna start with the basics, setting up a single Leaky Integrate and Fire neuron


# class boid_net():

#     def __init__(self):
#         start_scope()
#         self.A = 2.5
#         self.f = 10*Hz
#         self.tau = 5*ms
#         self.N = 5 #4 Neurons for input from 'sensors', 1 for output controlling direction

#         self.eqs =  '''
#         dv/dt = (1-v)/tau : 1
#         '''

#         # TimedArray appears to take in as input an array of values then the time interval.
#         self.G = NeuronGroup(self.N, self.eqs, threshold='v>1', reset='v=0', method='exact')
#         self.M = StateMonitor(self.G, variables=True, record=True)
#         self.S = Synapses(self.G, self.G, 'w : 0.25', on_pre='v_post += w')
#         self.S.connect(i=0, j=[1, 2, 3, 4])
    
#     def run(self, dt):
#         run(dt)

#     def plot(self):
#         plt.plot(self.M.t/ms, self.M.v[0], label='v')
#         plt.plot(self.M.t/ms, self.M.I[0], label='I')
#         plt.xlabel('Time (ms)')
#         plt.ylabel('v')
#         plt.legend(loc='best')
#         plt.show()

#     #take in as input the recorded I values, then update I_recorded so that 
#     def update(self, new_I):
#        self.G.run_regularly('self.I = new_I', dt=10*ms)

#     @network_operation(dt=10*ms)
#     def change_I(self, new_I):
#         self.G.I = new_I


#not working, let's go even more basic, one neuron, if it fires set velocity to 0
# class boid_net():

#     def __init__(self):
#         start_scope()

#         self.N = 1
#         self.tau = 10*ms

#         eqs =  '''
#         dv/dt = (1-v)/tau : 1
#         '''

#         self.G = NeuronGroup(N, eqs, threshold='v>1', reset='v=0', refractory=5*ms, method='exact')
#         self.M = SpikeMonitor(self.G, variables=True, record=True)

#     def run(self, dt):
#         run(dt)





#code for Hodgkin Huxley with randomized Amplitude for input I
# start_scope()
# group = NeuronGroup(1, eqs_HH,
#                     threshold='v > -40*mV',
#                     refractory='v > -40*mV',
#                     method='exponential_euler')
# group.v = El
# statemon = StateMonitor(group, 'v', record=True)
# spikemon = SpikeMonitor(group, variables='v')
# # we replace the loop with a run_regularly
# group.run_regularly('I = rand()*50*nA', dt=10*ms)
# run(50*ms)
# figure(figsize=(9, 4))
# # we keep the loop just to draw the vertical lines
# for l in range(5):
#     axvline(l*10, ls='--', c='k')
# axhline(El/mV, ls='-', c='lightgray', lw=3)
# plot(statemon.t/ms, statemon.v[0]/mV, '-b')
# plot(spikemon.t/ms, spikemon.v/mV, 'ob')
# xlabel('Time (ms)')
# ylabel('v (mV)')



#arbitrary python code change
# @network_operation(dt=10*ms)
# def change_I():
#     group.I = rand()*50*nA
# run(50*ms)
# figure(figsize=(9, 4))
# for l in range(5):
#     axvline(l*10, ls='--', c='k')
# axhline(El/mV, ls='-', c='lightgray', lw=3)
# plot(statemon.t/ms, statemon.v[0]/mV, '-b')
# plot(spikemon.t/ms, spikemon.v/mV, 'ob')
# xlabel('Time (ms)')
# ylabel('v (mV)');



# Arachnid
# Parameters
degree = 2 * pi / 360.
duration = 500*ms
R = 2.5*cm  # radius of scorpion
vr = 50*meter/second  # Rayleigh wave speed
phi = 144*degree  # angle of prey
A = 250*Hz
deltaI = .7*ms  # inhibitory delay
gamma = (22.5 + 45 * arange(8)) * degree  # leg angle
delay = R / vr * (1 - cos(phi - gamma))   # wave delay

# Wave (vector w)
time = arange(int(duration / defaultclock.dt) + 1) * defaultclock.dt
Dtot = 0.
w = 0.
for f in arange(150, 451)*Hz:
    D = exp(-(f/Hz - 300) ** 2 / (2 * (50 ** 2)))
    rand_angle = 2 * pi * rand()
    w += 100 * D * cos(2 * pi * f * time + rand_angle)
    Dtot += D
w = .01 * w / Dtot

# Rates from the wave
rates = TimedArray(w, dt=defaultclock.dt)

# Leg mechanical receptors
tau_legs = 1 * ms
sigma = .01
eqs_legs = """
dv/dt = (1 + rates(t - d) - v)/tau_legs + sigma*(2./tau_legs)**.5*xi:1
d : second
"""
legs = NeuronGroup(8, model=eqs_legs, threshold='v > 1', reset='v = 0',
                   refractory=1*ms, method='euler')
legs.d = delay
spikes_legs = SpikeMonitor(legs)

# Command neurons
tau = 1 * ms
taus = 1.001 * ms
wex = 7
winh = -2
eqs_neuron = '''
dv/dt = (x - v)/tau : 1
dx/dt = (y - x)/taus : 1 # alpha currents
dy/dt = -y/taus : 1
'''
neurons = NeuronGroup(8, model=eqs_neuron, threshold='v>1', reset='v=0',
                      method='exact')
synapses_ex = Synapses(legs, neurons, on_pre='y+=wex')
synapses_ex.connect(j='i')
synapses_inh = Synapses(legs, neurons, on_pre='y+=winh', delay=deltaI)
synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')
spikes = SpikeMonitor(neurons)

run(duration, report='text')

nspikes = spikes.count
phi_est = imag(log(sum(nspikes * exp(gamma * 1j))))
print("True angle (deg): %.2f" % (phi/degree))
print("Estimated angle (deg): %.2f" % (phi_est/degree))
rmax = amax(nspikes)/duration/Hz
polar(concatenate((gamma, [gamma[0] + 2 * pi])),
      concatenate((nspikes, [nspikes[0]])) / duration / Hz,
      c='k')
# axvline(phi, ls='-', c='g')
# axvline(phi_est, ls='-', c='b')
# show()