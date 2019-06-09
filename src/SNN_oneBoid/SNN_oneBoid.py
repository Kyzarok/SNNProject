import numpy, pyglet, time, random
from game import physicalWall, resources, load, util, boid, physicalObject
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
OB_1_X = 400 #random.randint(400, 1000)
OB_1_Y = 600 #random.randint(200, 700)
OB_1_SCALE = 1.0
OB_2_X = 800 #random.randint(200, 1000)
OB_2_Y = 300 #random.randint(200, 700)
OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='SNN Single Boid Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-10, y=Y_GOAL, batch=drawBatch)

boidList = []
obList = []



def init():
    global boidList, obList
    
    #init boids
    b_x = X_START #random.randint(X_START - 50, X_START + 50)
    b_y = Y_START #random.randint(Y_START - 50, Y_START + 50)

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

#much of the architecture is now in place, the main missing detail is the update of driveCurrent[] or w
#this is called the vector wave in other examples

def navigateBoids():
    #SNN takes in input of distances
    global boidList, obList

    for burd in boidList:
        b_x, b_y = burd.getPos()
        #driveCurrent = []
        for ob in obList:
            boidToSquare = ob.shortestDistance(b_x, b_y)
            angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
            #check between which two sensors this is, those two get spikes
            sensor_input = runSensors(angleToSquare)
            #basically the weight here is going to decide the frequency, and the minor difference in angle gap will decide the frequency to each sensor
            weight = 1/(boidToSquare ** 2)
            actuator_spikes = runAcutators(sensor_input)
            #spikes.i contains the indices of the neurons that spiked
            #spikes.t contains thee times they spiked
            #we want negative actuator spiking, so if it detects a wall, the opposite actuators 
            burd.response(actuator_spikes.i, actuator_spikes.t, weight)
            # actuator_spikes = RUN_EVERYTHING(angleToSquare)
            # print(actuator_spikes.i[:])


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
        obj.update((dt)


if __name__ == '__main__':
    #initialise the display
    init()

    # # Parameters
    # degree = 2 * pi / 360.
    # duration = 500*ms
    # R = 2.5*cm  # radius of scorpion
    # vr = 50*meter/second  # Rayleigh wave speed
    # phi = 0*degrees  # angle of prey
    # A = 250*Hz
    # deltaI = .7*ms  # inhibitory delay
    # gamma = (22.5 + 45 * arange(8)) * degree  # leg angle
    # delay = R / vr * (1 - cos(phi - gamma))   # wave delay

    # # Wave (vector w)
    # time = arange(int(duration / defaultclock.dt) + 1) * defaultclock.dt
    # Dtot = 0.
    # w = 0.
    # for f in arange(150, 451)*Hz:
    #     D = exp(-(f/Hz - 300) ** 2 / (2 * (50 ** 2)))
    #     rand_angle = 2 * pi * rand()
    #     w += 100 * D * cos(2 * pi * f * time + rand_angle)
    #     Dtot += D
    # w = .01 * w / Dtot

    # # Rates from the wave
    # rates = TimedArray(w, dt=defaultclock.dt)

    # # Leg mechanical receptors
    # tau_sensors = 1 * ms
    # eqs_sensors = """
    # dv/dt = (1 + rates(t - d) - v)/tau_sensors:1
    # d : second
    # """
    # wall_sensors = NeuronGroup(11, model=eqs_sensors, threshold='v > 1', reset='v = 0',
    #                 refractory=1*ms, method='euler')
    # wall_sensors.d = delay
    # spikes_sensors = SpikeMonitor(wall_sensors)

    # # Command neurons
    # tau = 1 * ms
    # taus = 1.001 * ms
    # wex = 7
    # winh = -2
    # eqs_actuator = '''
    # dv/dt = (x - v)/tau : 1
    # dx/dt = (y - x)/taus : 1 # alpha currents
    # dy/dt = -y/taus : 1
    # '''
    # actuators = NeuronGroup(11, model=eqs_actuator, threshold='v>1', reset='v=0',
    #                     method='exact')
    # synapses_ex = Synapses(wall_sensors, actuators, on_pre='y+=wex')
    # synapses_ex.connect(j='i')
    # synapses_inh = Synapses(wall_sensors, actuators, on_pre='y+=winh', delay=deltaI)
    # synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')
    # spikes = SpikeMonitor(actuators)

    pyglet.clock.schedule_interval(update, 5)
    pyglet.app.run()