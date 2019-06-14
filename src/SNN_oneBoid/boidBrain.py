from brian2 import *
import dill
import weakref
import copy
from multiprocessing import Process, Pipe

def RUN_NET(network_conn):
    start_scope()

    # Parameters

    initialised = False
    duration = 100 * 1000 * ms
    dt = 1500 * ms
    mod_val = dt
    step = 0.1*ms
    deltaI = .7*ms  # inhibitory delay

    dummy_arr = []
    dummy = [0] * 11
    time = arange(int(dt / (0.1*ms)) + 1) * (0.1*ms)
    for dummy_t in time:
        dummy_arr.append(dummy)

    i_arr_neg = dummy_arr
    i_arr_pos = dummy_arr

    I_neg = TimedArray(values=i_arr_neg, dt = step, name='I_neg')
    I_pos = TimedArray(values=i_arr_pos, dt = step, name='I_pos')

    tau_sensors = step
    eqs_avoid = '''
    dv/dt = (I_neg(t, i) - v)/tau_sensors : 1
    '''
    negative_sensors = NeuronGroup(11, model=eqs_avoid, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler', name='negative_sensors')
    neg_spikes_sensors = SpikeMonitor(negative_sensors, name='neg_spikes_sensors')


    eqs_attract= '''
    dv/dt = (I_pos(t, i) - v)/tau_sensors : 1
    '''
    positive_sensors = NeuronGroup(11, model=eqs_attract, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler', name='positive_sensors')
    pos_spikes_sensors = SpikeMonitor(positive_sensors, name='pos_spikes_sensors')

    # Command neurons
    tau = 1 * ms
    taus = 1.001 * ms
    wex = 5
    winh = -2
    eqs_actuator = '''
    dv/dt = (x - v)/tau : 1
    dx/dt = (y - x)/taus : 1 # alpha currents
    dy/dt = -y/taus : 1
    '''
    actuators = NeuronGroup(11, model=eqs_actuator, threshold='v>2', reset='v=0', method='exact', name='actuators')
    synapses_ex = Synapses(negative_sensors, actuators, on_pre='y+=winh', name='synapses_ex')
    synapses_ex.connect(j='i')
    synapses_inh = Synapses(negative_sensors, actuators, on_pre='y+=wex', delay=deltaI, name='synapses_inh')
    synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')

    WEXCITE = 7

    synapses_EXCITE = Synapses(positive_sensors, actuators, on_pre='y+=WEXCITE', name='synapses_EXCITE')
    synapses_EXCITE.connect(j='i')

    actuator_spikes = SpikeMonitor(actuators, name='actuator_spikes')

    @network_operation(dt=dt)
    def change_I():
        print('actuator_spikes.count: ')
        print(str(actuator_spikes.count))
        # dill.loads(dill.dumps(weakref.WeakKeyDictionary()))
        # dill.loads(dill.dumps(weakref.WeakValueDictionary()))
        # #gets past here
        # dill.loads(dill.dumps(weakref.ref(actuator_spikes)))
        # #STUFF GOES WRONG FROM THE ABOVE LINE
        # dill.loads(dill.dumps(weakref.ref(SpikeMonitor(actuators, name='actuator_spikes'))))
        # dill.loads(dill.dumps(weakref.proxy(actuator_spikes)))
        # dill.loads(dill.dumps(weakref.proxy(SpikeMonitor(actuators, name='actuator_spikes'))))
        spikes = str(actuator_spikes.count)
        # for i in range(11):
        #     spikes.append(actuator_spikes.count[i])
        #send spikes to physics
        # spikes = None
        # with open('hackySolution.pkl', 'wb') as file:
        #     dill.dump(actuator_spikes.count, file)
        # with open('hackySolution.pkl', 'rb') as file:
        #     spikes = dill.load(file)

        network_conn.send(spikes)
        print('network send')
        # actuator_spikes.count[:] = 0
        I_avoid, I_attract = network_conn.recv()
        print('network receive')
        i_arr_neg[:] = I_avoid
        i_arr_pos[:] = I_attract



    print('BEGIN NEURAL NETWORK')
    run(duration)
