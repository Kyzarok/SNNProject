from brian2 import *
from game import util

def RUN_NET(network_conn):
    start_scope()

    # Parameters

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
    dv/dt = (I_neg(t % mod_val, i) - v)/tau_sensors : 1
    '''
    negative_sensors = NeuronGroup(11, model=eqs_avoid, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler', name='negative_sensors')
    neg_spikes_sensors = SpikeMonitor(negative_sensors, name='neg_spikes_sensors')


    eqs_attract= '''
    dv/dt = (I_pos(t % mod_val, i) - v)/tau_sensors : 1
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

    def create_change_I(spike_data, i_arr_n, i_arr_p):
        @network_operation(dt=dt)
        def change_I():
            #send spikes to physics
            spikes = spike_data[:]
            print('spikes:')
            print(spikes)
            network_conn.send(spikes)
            print('network send')
            # actuator_spikes = NEEDS TO BECOME 0
            I_avoid, I_attract = network_conn.recv()
            print('network receive')
            i_arr_n = I_avoid
            i_arr_p = I_attract
        return change_I
    
    change_I = create_change_I(actuator_spikes.count, i_arr_neg, i_arr_pos)



    print('BEGIN NEURAL NETWORK')
    run(duration)
    # print('run err')

    # print("negative_sensors.count: ")
    # print(neg_spikes_sensors.count)
    # print("positive_sensors.count: ")
    # print(pos_spikes_sensors.count)
