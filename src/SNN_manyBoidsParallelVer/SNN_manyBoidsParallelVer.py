import numpy, pyglet, time, random
from game import physicalObject, physicalWall, boid, resources, load, util
from brian2 import *
import multiprocessing as mp
from pyglet.gl import *
from matplotlib import pyplot


#dimensions for window
WIDTH = 1200 #3000
HEIGHT = 900 #1500

#start and end coords
X_START = 50 #50 #400 #50
Y_START = 850 #1450 #850 #100 #850 #600
X_GOAL = 1100 #2900#1100#100#
Y_GOAL = 100 #100#600#

#coords and dimensions for rectangular obstacle
OB_1_X = 400#600#300#600#400 
OB_1_Y = 600#450#650#450#600 
OB_1_SCALE = 1.0
OB_2_X = 800#750#800 
OB_2_Y = 250#500#250 
OB_2_SCALE = 0.5

# #BIGMAP OBSTACLES
# OB_1_X = 600
# OB_1_Y = 1200
# OB_1_SCALE = 1.0
# OB_2_X = 1000
# OB_2_Y = 1000
# OB_2_SCALE = 0.5
# OB_3_X = 2000
# OB_3_Y = 1000
# OB_3_SCALE = 2.0
# OB_4_X = 2500
# OB_4_Y = 500
# OB_4_SCALE = 1.0
# OB_5_X = 1500
# OB_5_Y = 600
# OB_5_SCALE = 1.0
# OB_6_X = 850
# OB_6_Y = 750
# OB_6_SCALE = 0.5
# OB_7_X = 1250
# OB_7_Y = 1000
# OB_7_SCALE = 0.25
# OB_8_X = 1900
# OB_8_Y = 400
# OB_8_SCALE = 0.5
# OB_9_X = 1150
# OB_9_Y = 500
# OB_9_SCALE = 0.5

# # #values for getting trapped
# OB_1_X = 500 
# OB_1_Y = 350 
# OB_1_SCALE = 1.0
# OB_2_X = 600 
# OB_2_Y = 550
# OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='SNN Multiple Boids Maze Navigation', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

boidList = []
finished_boids = []
obList = []
taken_files = 0
initialised = False

def init():
    global boidList, obList
    b_x = X_START 
    b_y = Y_START
    maverick = boid.Boid(x=b_x, y=b_y, batch=drawBatch)
    maverick.setTarget(X_GOAL, Y_GOAL)
    goose = boid.Boid(x=b_x, y=b_y-50, batch=drawBatch)
    goose.setTarget(X_GOAL, Y_GOAL)
    mehve = boid.Boid(x=b_x, y=b_y-100, batch=drawBatch)
    mehve.setTarget(X_GOAL, Y_GOAL)
    red_five = boid.Boid(x=b_x+50, y=b_y, batch=drawBatch)
    red_five.setTarget(X_GOAL, Y_GOAL)
    serenity = boid.Boid(x=b_x+50, y=b_y-50, batch=drawBatch)
    serenity.setTarget(X_GOAL, Y_GOAL)
    nirvash = boid.Boid(x=b_x+50, y=b_y-100, batch=drawBatch)
    nirvash.setTarget(X_GOAL, Y_GOAL)

    #init obstacles
    square_1 = physicalWall.Square(x=OB_1_X, y=OB_1_Y, batch=drawBatch)
    square_1.setScale(OB_1_SCALE)
    square_2 = physicalWall.Square(x=OB_2_X, y=OB_2_Y, batch=drawBatch)
    square_2.setScale(OB_2_SCALE)
    # square_3 = physicalWall.Square(x=OB_3_X, y=OB_3_Y, batch=drawBatch)
    # square_3.setScale(OB_3_SCALE)
    # square_4 = physicalWall.Square(x=OB_4_X, y=OB_4_Y, batch=drawBatch)
    # square_4.setScale(OB_4_SCALE)
    # square_5 = physicalWall.Square(x=OB_5_X, y=OB_5_Y, batch=drawBatch)
    # square_5.setScale(OB_5_SCALE)    
    # square_6 = physicalWall.Square(x=OB_6_X, y=OB_6_Y, batch=drawBatch)
    # square_6.setScale(OB_6_SCALE)
    # square_7 = physicalWall.Square(x=OB_7_X, y=OB_7_Y, batch=drawBatch)
    # square_7.setScale(OB_7_SCALE)    
    # square_8 = physicalWall.Square(x=OB_8_X, y=OB_8_Y, batch=drawBatch)
    # square_8.setScale(OB_8_SCALE)    
    # square_9 = physicalWall.Square(x=OB_9_X, y=OB_9_Y, batch=drawBatch)
    # square_9.setScale(OB_9_SCALE)


    obList = [square_1, square_2]#, square_3, square_4, square_5, square_6, square_7, square_8, square_9]
    boidList = [maverick, goose, mehve, red_five, serenity, nirvash]

@gameWindow.event
def on_draw():
    global finished_boids
    gameWindow.clear()
    if boidList == []:
        glBegin(GL_LINES)
        for f in finished_boids:
            coords = f.get_record()
            for i in range(len(coords)-1):
                x_0, y_0 = coords[i]
                x_1, y_1 = coords[i+1]
                glVertex2i(int(x_0), int(y_0))
                glVertex2i(int(x_1), int(y_1))
        glEnd()
        for ob in obList:
            ob.draw()
    else:
        drawBatch.draw()

def navigateBoid(physics_conn):
    global boidList, initialised, finished_boids
    index = 0
    if initialised:
        for burd in boidList:
            if  not (burd in finished_boids):
                #receive spikes from network
                actuator_spikes_literal = physics_conn[index].recv()
                print('physics receive')
                burd.num_response(actuator_spikes_literal)
                index += 1
            else:
                index+=1

def updateInput(dt, physics_conn):
    global boidList, obList, finished_boids
    I_avoid = None
    I_attract = None

    index = 0
    for burd in boidList:
        if  burd in finished_boids:
            physics_conn[index].send([0, 0, 'ended'])
            index += 1
        else:
            b_x, b_y = burd.getPos()
            angleList = []
            weightList = []
            typeList = []
            for ob in obList:
                boidToSquare = ob.shortestDistance(b_x, b_y)
                angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
                if boidToSquare < 150*ob.getScale():
                    weightList.append(1/(boidToSquare**2))
                    angleList.append(angleToSquare)
                    typeList.append('w')

            for otherBurds in boidList:
                if burd != otherBurds:
                    b_x, b_y = otherBurds.getPos()
                    boidToBoid = burd.shortestDistance(b_x, b_y)
                    angleToBoid = burd.angleFromBoidToBoid(b_x, b_y)
                    if boidToBoid < 100*otherBurds.getScale():
                        weightList.append(1/(boidToBoid**2))
                        angleList.append(angleToBoid)
                        typeList.append('b')

            op = burd.getOptimalHeading()
            I_avoid = burd.avoid_sensor_input(dt, angleList, weightList, typeList)
            I_attract = burd.optimal_sensor_input(dt, op)
            physics_conn[index].send([I_avoid, I_attract, index])
            print('physics send')
            index += 1

def checkGoal():
    global finished_boids, boidList, taken_files
    for burd in boidList:
        b_x, b_y = burd.getPos()
        if X_GOAL-20 <=b_x <= X_GOAL+20 and Y_GOAL-20 <=b_y <= Y_GOAL+20:
            # TO SAVE DATA UN COMMENT THE LOWER NEXT TWO LINES
            burd.text_record_spikes(str(taken_files))
            burd.text_record_coords(str(taken_files))
            boidList.remove(burd)
            finished_boids.append(burd)
            taken_files += 1

    
def update(dt, physics_conn):
    dt = 0.08
    global boidList, obList, initialised, finished_boids

    if boidList == []:
        time.sleep(8)

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

    checkGoal()

    navigateBoid(physics_conn)

    initialised = True

    for obj in gameList:
        obj.update(dt)

    updateInput(dt, physics_conn)

def RUN_PHYSICS(physics_conn):
    init()
    pyglet.clock.schedule_interval(update, 0.08, physics_conn)
    pyglet.app.run()

def RUN_NET(network_conn, brain_index):
    start_scope()

    # Parameters
    dt = 80 * ms
    modval = dt
    my_default = 1.0 * ms
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

    dt = len(i_arr_pos) * my_default

    
    #Sensor Neurons
    tau_sensors = my_default
    eqs_avoid = '''
    dv/dt = (I_neg(t%modval, i) - v)/tau_sensors : 1
    '''
    negative_sensors = NeuronGroup(11, model=eqs_avoid, threshold='v > 2.0', reset='v = 0', refractory=1*ms, method='euler', name='negative_sensors')
    neg_spikes_sensors = SpikeMonitor(negative_sensors, name='neg_spikes_sensors')

    eqs_attract = '''
    dv/dt = (I_pos(t%modval, i) - v)/tau_sensors : 1
    '''
    positive_sensors = NeuronGroup(11, model=eqs_attract, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler', name='positive_sensors')
    pos_spikes_sensors = SpikeMonitor(positive_sensors, name='pos_spikes_sensors')


    # Actuator neurons
    tau = 1.0 * ms
    taus = 1.001 * ms
    w_ex = 4
    w_inh = -6
    eqs_actuator = '''
    dv/dt = (x - v)/tau : 1
    dx/dt = (y - x)/taus : 1 # alpha currents
    dy/dt = -y/taus : 1
    '''
    actuators = NeuronGroup(11, model=eqs_actuator, threshold='v>1', reset='v=0', method='exact', name='actuators')
    synapses_inh = Synapses(negative_sensors, actuators, on_pre='y+=w_inh', name='synapses_inh')
    synapses_inh.connect(j='i')
    synapses_ex = Synapses(negative_sensors, actuators, on_pre='y+=w_ex', delay=deltaI, name='synapses_ex')
    synapses_ex.connect('abs(((j - i) % N_post) - N_post/2) <= 1')

    W_OPTIMAL = 6

    synapses_OPTIMAL= Synapses(positive_sensors, actuators, on_pre='y+=W_OPTIMAL', name='synapses_OPTIMAL')
    synapses_OPTIMAL.connect(j='i')

    actuator_spikes = SpikeMonitor(actuators, name='actuator_spikes')

    @network_operation(dt=dt)
    def change_I():
        new_spikes = str(actuator_spikes.count)
        new_spikes = new_spikes + brain_index
        network_conn.send(new_spikes)
        print('network send')
        I_avoid, I_attract, index = network_conn.recv()
        if index == 'ended':
            stop()
        print('network receive')
        I_neg.values[:] = I_avoid
        I_pos.values[:] = I_attract


    print('BEGIN NEURAL NETWORK')
    run(1000000*dt)
    print('SNN STOPPED')


if __name__ == '__main__':
    mp.set_start_method('spawn')
    network_conn_0, physics_conn_0 = mp.Pipe()
    network_conn_1, physics_conn_1 = mp.Pipe()
    network_conn_2, physics_conn_2 = mp.Pipe()
    network_conn_3, physics_conn_3 = mp.Pipe()
    network_conn_4, physics_conn_4 = mp.Pipe()
    network_conn_5, physics_conn_5 = mp.Pipe()
    physics_conn = [physics_conn_0, physics_conn_1, physics_conn_2, physics_conn_3, physics_conn_4, physics_conn_5]
    network_conn = [network_conn_0, network_conn_1, network_conn_2, network_conn_3, network_conn_4, network_conn_5]

    print('SETTING PHYSICS')
    #dummy send for first iteration
    for n in network_conn:
        n.send(None)
    p_core = mp.Process(target=RUN_PHYSICS, args=(physics_conn,))

    print('SETTING NETWORK')
    p_0 = mp.Process(target=RUN_NET, args=(network_conn_0, '0', ))
    p_1 = mp.Process(target=RUN_NET, args=(network_conn_1, '1', ))
    p_2 = mp.Process(target=RUN_NET, args=(network_conn_2, '2', ))
    p_3 = mp.Process(target=RUN_NET, args=(network_conn_3, '3', ))
    p_4 = mp.Process(target=RUN_NET, args=(network_conn_4, '4', ))
    p_5 = mp.Process(target=RUN_NET, args=(network_conn_5, '5', ))
    
    print('STARTING PHYSICS')
    p_core.start()

    print('STARTING NETWORKS')
    p_0.start()
    p_1.start()
    p_2.start()
    p_3.start()
    p_4.start()
    p_5.start()
