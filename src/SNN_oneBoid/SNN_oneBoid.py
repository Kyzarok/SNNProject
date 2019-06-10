import numpy, pyglet, time, random
from game import physicalObject, physicalWall, boid, resources, load, util
from brian2 import *

#dimensions for window
WIDTH = 1200
HEIGHT = 900

#start and end coords, WIDTH-
X_START = 50
Y_START = 850
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


def run_SNN(I_values, tau, dt):
    start_scope()

    # Parameters
    duration = dt
    deltaI = .7*ms  # inhibitory delay

    tau_sensors = defaultclock.dt
    eqs_sensors = """
    dv/dt = (1 + I_values(t, i) - v)/tau_sensors:1
    """
    wall_sensors = NeuronGroup(11, model=eqs_sensors, threshold='v > 1', reset='v = 0', refractory=1*ms, method='euler')
    spikes_sensors = SpikeMonitor(wall_sensors)

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
    actuators = NeuronGroup(11, model=eqs_actuator, threshold='v>1', reset='v=0',
                        method='exact')
    synapses_ex = Synapses(wall_sensors, actuators, on_pre='y+=wex')
    synapses_ex.connect(j='i')
    synapses_inh = Synapses(wall_sensors, actuators, on_pre='y+=winh', delay=deltaI)
    synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')
    spikes = SpikeMonitor(actuators)

    run(duration)

    print(spikes.i)
    print(spikes_sensors.i)

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

def navigateBoids():
    global boidList, obList

    dt = 500*ms
    
    for burd in boidList:
        b_x, b_y = burd.getPos()
        for ob in obList:
            boidToSquare = ob.shortestDistance(b_x, b_y)
            angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
            weight = 1/(boidToSquare**2)
            #send sensor input, receive actuator output
            I_values, tau = burd.drive_currents(dt, angleToSquare, weight)
            actuator_spikes = run_SNN(I_values, tau, dt)
            #run physics
            burd.wall_response(actuator_spikes.i, actuator_spikes.t, boidToSquare)

    
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

    navigateBoids()

    for obj in gameList:
        obj.update(dt)


if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 10)#call once every 5 seconds
    pyglet.app.run()