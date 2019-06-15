import numpy, pyglet, time, random
from game import physicalObject, physicalWall, boid, resources, load, util
from brian2 import *
import multiprocessing as mp
# from multiprocessing import Process, Pipe


#dimensions for window
WIDTH = 1200
HEIGHT = 900

#start and end coords, WIDTH-
X_START = 50 #400 #50
Y_START = 850 #100 #850 #600
X_GOAL = 1100
Y_GOAL = 100

#coords and dimensions for rectangular obstacle
OB_1_X = 400 #random.randint(200, 1000)
OB_1_Y = 600 #random.randint(200, 700)
OB_1_SCALE = 1.0
OB_2_X = 800 #random.randint(200, 1000) #350
OB_2_Y = 250 #random.randint(200, 700) #450
OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

#this can easily not be a global dude fix it
boidStillFlying = True

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='SNN Single Boid Maze Navigation', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

boidList = []
obList = []
initialised = False

def init():
    global boidList, obList
    b_x = X_START 
    b_y = Y_START
    maverick = boid.Boid(x=b_x, y=b_y, batch=drawBatch)
    #init obstacles
    square_1 = physicalWall.Square(x=OB_1_X, y=OB_1_Y, batch=drawBatch)
    square_1.setScale(OB_1_SCALE)
    square_2 = physicalWall.Square(x=OB_2_X, y=OB_2_Y, batch=drawBatch)
    square_2.setScale(OB_2_SCALE)
    obList = [square_1, square_2]
    boidList = [maverick]

@gameWindow.event
def on_draw():
    gameWindow.clear()
    drawBatch.draw()

def navigateBoid(actuator_spikes_literal):
    global boidList, initialised
    if initialised:
        for burd in boidList:
            burd.num_response(actuator_spikes_literal)

def updateInput(dt):
    global boidList, obList
    I_avoid = None
    I_attract = None
    for burd in boidList:
        b_x, b_y = burd.getPos()
        angleList = []
        weightList = []
        for ob in obList:
            boidToSquare = ob.shortestDistance(b_x, b_y)
            angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
            if boidToSquare < 150:
                weight = 1/((boidToSquare)**2)
                weightList.append(weight)
                angleList.append(angleToSquare)
        op = burd.getOptimalHeading()
        I_avoid = burd.wall_sensor_input(dt, angleList, weightList)
        I_attract = burd.optimal_sensor_input(dt, op)
    return I_avoid, I_attract
    
def update(dt, physics_conn):
    global boidList, obList, initialised

    gameList = obList + boidList
    for i in range(len(gameList)):
        for j in range(i+1, len(gameList)):
            gameObj_1 = gameList[i]
            gameObj_2 = gameList[j]
        if not gameObj_1.collision and not gameObj_2.collision:
            if gameObj_1.collidesWith(gameObj_2):
                gameObj_1.handleCollisionWith(gameObj_2)
                gameObj_2.handleCollisionWith(gameObj_1)
                print('COLLISION')
                exit()


    #receive spikes from network
    new_spikes = physics_conn.recv()
    print('physics receive')
    #print(new_spikes)

    navigateBoid(new_spikes)

    initialised = True

    dt = 1

    for obj in gameList:
        obj.update(dt)

    I_values = updateInput(dt)
    
    physics_conn.send(I_values)
    print('physics send')

def RUN_PHYSICS(physics_conn):
    init()
    pyglet.clock.schedule_interval(update, 1.1, physics_conn)
    pyglet.app.run()

def RUN_NET(network_conn):
    start_scope()

    # Parameters
    
    dt = 1000 * ms
    modval = dt
    my_default = 0.1 * ms
    deltaI = .7*ms  # inhibitory delay

    dummy_arr = []
    dummy = [0] * 11
    time = arange(int(dt / my_default) + 1) * my_default

    for dummy_t in time:
        dummy_arr.append(dummy)

    i_arr_neg = dummy_arr
    i_arr_pos = dummy_arr


    I_neg = TimedArray(values=i_arr_neg, dt = my_default, name='I_neg')
    I_pos = TimedArray(values=i_arr_pos, dt = my_default, name='I_pos')

    tau_sensors = my_default
    eqs_avoid = '''
    dv/dt = (I_neg(t%modval, i) - v)/tau_sensors : 1
    '''
    negative_sensors = NeuronGroup(11, model=eqs_avoid, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler', name='negative_sensors')
    neg_spikes_sensors = SpikeMonitor(negative_sensors, name='neg_spikes_sensors')

    eqs_attract = '''
    dv/dt = (I_pos(t%modval, i) - v)/tau_sensors : 1
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
        print("neg_spike_sensors: ")
        print(neg_spikes_sensors.count)
        print("pos_spike_sensors: ")
        print(pos_spikes_sensors.count)
        print('actuator_spikes.count: ')
        print(actuator_spikes.count)
        spikes = str(actuator_spikes.count)
        network_conn.send(spikes)
        print('network send')    
        I_avoid, I_attract = network_conn.recv()
        print('network receive')
        i_arr_neg[:] = I_avoid
        i_arr_pos[:] = I_attract
        I_neg = TimedArray(values=i_arr_neg, dt = my_default, name='I_neg')
        I_pos = TimedArray(values=i_arr_pos, dt = my_default, name='I_pos')


    print('BEGIN NEURAL NETWORK')
    run(100*dt)
    print('SNN STOPPED')

if __name__ == '__main__':
    mp.set_start_method('spawn')
    network_conn, physics_conn = mp.Pipe()
    print('SETTING PHYSICS')
    #dummy send for first iteration
    network_conn.send(None)
    p_1 = mp.Process(target=RUN_PHYSICS, args=(physics_conn,))
    print('SETTING NETWORK')
    p_2 = mp.Process(target=RUN_NET, args=(network_conn,))
    print('STARTING PHYSICS')
    p_1.start()
    print('STARTING NETWORK')
    p_2.start()
