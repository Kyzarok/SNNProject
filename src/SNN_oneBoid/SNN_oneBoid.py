import numpy, pyglet, time, random
from game import physicalObject, physicalWall, boid, resources, load, util
from brian2 import *

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
OB_2_X = 800 #random.randint(200, 1000)
OB_2_Y = 250 #random.randint(200, 700)
OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

#this can easily not be a global dude fix it
boidStillFlying = True

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='SNN Single Boid Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

boidList = []
obList = []


def run_SNN(I_avoid, I_attract, dt):
    start_scope()

    # Parameters
    duration = dt
    deltaI = .7*ms  # inhibitory delay

    tau_sensors = 0.1*ms
    eqs_avoid = '''
    dv/dt = (I - v)/tau_sensors : 1
    I = I_avoid(t, i) : 1
    '''
    negative_sensors = NeuronGroup(11, model=eqs_avoid, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler')
    neg_spikes_sensors = SpikeMonitor(negative_sensors)
    

    eqs_attract= '''
    dv/dt = (I - v)/tau_sensors : 1
    I = I_attract(t, i) : 1
    '''
    positive_sensors = NeuronGroup(11, model=eqs_attract, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler')
    pos_spikes_sensors = SpikeMonitor(positive_sensors)

    # Command neurons
    tau = 1 * ms
    taus = 1.001 * ms
    wex = 7
    winh = -2
    eqs_actuator = '''
    dv/dt = (x - v)/tau : 1
    dx/dt = (y - x)/taus : 1 # alpha currents
    dy/dt = -y/taus : 1
    '''
    actuators = NeuronGroup(11, model=eqs_actuator, threshold='v>2', reset='v=0', method='exact')
    synapses_ex = Synapses(negative_sensors, actuators, on_pre='y+=winh')
    synapses_ex.connect(j='i')
    synapses_inh = Synapses(negative_sensors, actuators, on_pre='y+=wex', delay=deltaI)
    synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')

    WEXCITE = 6

    synapses_EXCITE = Synapses(positive_sensors, actuators, on_pre='y+=WEXCITE')
    synapses_EXCITE.connect(j='i')


    spikes = SpikeMonitor(actuators)

    run(duration)

    # print(spikes.i)
    print("negative_sensors.count: ")
    print(neg_spikes_sensors.count)
    print("positive_sensors.count: ")
    print(pos_spikes_sensors.count)
    # print("actuator_spikes_count: ")
    # print(spikes.count)

    return spikes

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
    obList = [square_1]#, square_2]
    boidList = [maverick]

@gameWindow.event
def on_draw():
    gameWindow.clear()
    drawBatch.draw()

def navigateBoids(dt):
    dt = dt * 1000 *ms
    global boidList, obList
    for burd in boidList:
        b_x, b_y = burd.getPos()
        angleList = []
        weightList = []
        for ob in obList:
            boidToSquare = ob.shortestDistance(b_x, b_y)
            angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
            weight = 1/((boidToSquare)**2)
            angleList.append(angleToSquare)
            weightList.append(weight)
        op = burd.getOptimalHeading()
        # I_values = burd.drive_currents(dt, angleList, weightList, op)

        I_avoid = burd.wall_sensor_input(dt, angleList, weightList)
        I_attract = burd.optimal_sensor_input(dt, op)
        #send sensor input, receive actuator output
        actuator_spikes = run_SNN(I_avoid, I_attract, dt)
        #run physics
        burd.response(actuator_spikes, boidToSquare)

    
def update(dt):
    global boidList, obList

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
    dt = 0.5
    navigateBoids(dt)

    for obj in gameList:
        obj.update(dt)


if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 3)
    pyglet.app.run()