import numpy, pyglet, time, random
from game import physicalWall, boid_brain, resources, load, util, boid, physicalObject
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


##################################################################################
############################# SNN STUFF HERE #####################################
##################################################################################
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

rates = TimedArray(w, dt=defaultclock.dt)

tau_sensor= 1 * ms
eqs_sensors = """
dv/dt = (1 + rates(t - d) - v)/tau_sensor:1
d : second
"""
wall_sensors = NeuronGroup(11, model=eqs_sensors, threshold='v > 1', reset='v = 0', refractory=1*ms, method='euler')

tau = 1 * ms
taus = 1.001 * ms
wex = 7
winh = -2
eqs_neuron = '''
dv/dt = (x - v)/tau : 1
dx/dt = (y - x)/taus : 1 # alpha currents
dy/dt = -y/taus : 1
'''
actuators = NeuronGroup(11, model=eqs_neuron, threshold='v>1', reset='v=0', method='exact')

spikes = SpikeMonitor(actuators)

indices = [3, 4] #arbitrary start
times = [0*ms, 0*ms]
sensor_input = SpikeGeneratorGroup(11, indices, times)


def runAcutators(sensor_input, dt):
    global rates, tau_sensor, wall_sensors, actuators, wex, winh, deltaI
    rates = TimedArray(sensor_input.i[:], sensor_input.t[:])
    eqs_sensors = """
    dv/dt = (1 + rates(t - d) - v)/tau_sensor:1
    d : second
    """
    wall_sensors = NeuronGroup(11, model=eqs_sensors, threshold='v > 1', reset='v = 0', refractory=1*ms, method='euler')

    synapses_ex = Synapses(wall_sensors, actuators, on_pre='y+=wex')
    synapses_ex.connect(j='i')
    synapses_inh = Synapses(wall_sensors, actuators, on_pre='y+=winh', delay=deltaI)
    synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')

    print('ABOUT TO RUN ACTUATORS')
    run(dt*1000*ms)
    print('RAN ACTUATORS')
    return spikes
    
def runSensors(angleToSquare, dt):
    global indices, times, sensor_input
    #30 degrees is math.pi/6
    spike_1 = 0
    spike_2 = 0
    for i in range(10):
        current_orientation = -5*math.pi/6 + i*math.pi/6
        if current_orientation <= angleToSquare < current_orientation + math.pi/6:
            spike_1 = i
            spike_2 = i+1

    #input = SpikeGeneratorGroup(number_of_neurons_in_group, array_of_indices_of_neurons_that_will_fire, array_of_times_that_the_neurons_the_neurons_will_fire_a_spike)
    for i
    indices = array([spike_1, spike_2])
    times = array([x+(dt*ms) for x in times])*ms
    sensor_input.set_spikes(indices, times)
    return sensor_input

##################################################################################
##################################################################################
##################################################################################


# def RUN_EVERYTHING(angleToSquare):
#     degree = 2 * pi / 360.
#     duration = 500*ms
#     R = 2.5*cm  # radius of scorpion
#     vr = 50*meter/second  # Rayleigh wave speed
#     phi = math.degrees(angleToSquare)*degree  # angle of prey
#     A = 250*Hz
#     deltaI = .7*ms  # inhibitory delay
#     gamma = (22.5 + 45 * arange(8)) * degree  # leg angle
#     delay = R / vr * (1 - cos(phi - gamma))   # wave delay

#     # Wave (vector w)
#     time = arange(int(duration / defaultclock.dt) + 1) * defaultclock.dt
#     Dtot = 0.
#     w = 0.
#     for f in arange(150, 451)*Hz:
#         D = exp(-(f/Hz - 300) ** 2 / (2 * (50 ** 2)))
#         rand_angle = 2 * pi * rand()
#         w += 100 * D * cos(2 * pi * f * time + rand_angle)
#         Dtot += D
#     w = .01 * w / Dtot

#     # Rates from the wave
#     rates = TimedArray(w, dt=defaultclock.dt)

#     # Leg mechanical receptors
#     tau_legs = 1 * ms
#     sigma = .01
#     eqs_legs = """
#     dv/dt = (1 + rates(t - d) - v)/tau_legs + sigma*(2./tau_legs)**.5*xi:1
#     d : second
#     """
#     legs = NeuronGroup(8, model=eqs_legs, threshold='v > 1', reset='v = 0',
#                     refractory=1*ms, method='euler')
#     legs.d = delay
#     spikes_legs = SpikeMonitor(legs)

#     # Command neurons
#     tau = 1 * ms
#     taus = 1.001 * ms
#     wex = 7
#     winh = -2
#     eqs_neuron = '''
#     dv/dt = (x - v)/tau : 1
#     dx/dt = (y - x)/taus : 1 # alpha currents
#     dy/dt = -y/taus : 1
#     '''
#     neurons = NeuronGroup(8, model=eqs_neuron, threshold='v>1', reset='v=0',
#                         method='exact')
#     synapses_ex = Synapses(legs, neurons, on_pre='y+=wex')
#     synapses_ex.connect(j='i')
#     synapses_inh = Synapses(legs, neurons, on_pre='y+=winh', delay=deltaI)
#     synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')
#     spikes = SpikeMonitor(neurons)

#     run(duration, report='text')

#     return spikes

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

def navigateBoids(dt):
    #SNN takes in input of distances
    global boidList, obList

    for burd in boidList:
        b_x, b_y = burd.getPos()
        #driveCurrent = []
        for ob in obList:
            boidToSquare = ob.shortestDistance(b_x, b_y)
            angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
            #check between which two sensors this is, those two get spikes
            sensor_input = runSensors(angleToSquare, dt)
            #basically the weight here is going to decide the frequency, and the minor difference in angle gap will decide the frequency to each sensor
            weight = 1/(boidToSquare ** 2)
            actuator_spikes = runAcutators(sensor_input, dt)
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

    navigateBoids((dt*0.9)/2)

    for obj in gameList:
        obj.update((dt*0.9)/2)


if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 5)
    pyglet.app.run()
