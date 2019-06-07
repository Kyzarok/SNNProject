import pyglet, math, random
from game import resources, util, boid
from brian2 import *

class SmartBoid(boid.Boid):

    def __init__(self):
        super(SmartBoid, self).__init__()
        self.deltaI = .7*ms  # inhibitory delay

        #spike rates
        self.rates = None

        #for there to be enough neurons, we need to think carefully
        #we can do either different groups of neurons for different things, bird sensors, wall sensors, etc
        #or we can do one sensor group for all
        #first step is one sensor group for all as we're only considering obstacles, not other boids, for now

        #so first we need to pick the number of sensors, looking at papers on bird eyes (https://web.archive.org/web/20081217154759/http://www.csulb.edu/~efernand/visualecol/Avian%20vision.pdf)
        #they say that bird of prey have 150 degs, pigeons have 300 degs. As we're thinking about swarms, and birds of prey as described here don't often swarm but are in fact territorial
        #we will go with the pigeon analogy of a wide field of vision. This still allows for a 60 degree gap, which we previously thought about and programmed in but got the value wrong
        #This will mean 150 degrees on either side, let's say we want one directly forwards. 150/30 = 5, so a total of 9 sensors spread apart every 30 degs makes sense

        self.tau_sensor= 1 * ms
        self.eqs_sensors = """
        dv/dt = (1 + self.rates(t - d) - v)/tau_sensor:1
        d : second
        """
        self.wall_sensors = NeuronGroup(9, model=self.eqs_sensors, threshold='v > 1', reset='v = 0',
                   refractory=1*ms, method='euler')

        spikes_sensors = SpikeMonitor(self.wall_sensors)

        self.tau = 1 * ms
        self.taus = 1.001 * ms
        self.wex = 7
        self.winh = -2
        eqs_neuron = '''
        dv/dt = (x - v)/self.tau : 1
        dx/dt = (y - x)/self.taus : 1 # alpha currents
        dy/dt = -y/self.taus : 1
        '''
        self.actuators = NeuronGroup(9, model=eqs_neuron, threshold='v>1', reset='v=0',
                            method='exact')
        self.synapses_ex = Synapses(self.wall_sensors, self.actuators, on_pre='y+=self.wex')
        self.synapses_ex.connect(j='i')
        self.synapses_inh = Synapses(self.wall_sensors, self.actuators, on_pre='y+=self.winh', delay=self.deltaI)
        self.synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')


    def run(self, wlist, dt):
        self.rates = TimedArray(wlist, dt=defaultclock.dt)
        self.wall_sensors.model = """
        dv/dt = (1 + self.rates(t - d) - v)/self.tau_sensor:1
        d : second
        """
        self.synapses_ex = Synapses(self.wall_sensors, self.actuators, on_pre='y+=self.wex')
        self.synapses_ex.connect(j='i')
        self.synapses_inh = Synapses(self.wall_sensors, self.actuators, on_pre='y+=self.winh', delay=self.deltaI)
        self.synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')

        spikes = SpikeMonitor(self.actuators)

        run(dt)

        return spikes



