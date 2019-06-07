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
OB_1_X = 400 #random.randint(400, 1000)
OB_1_Y = 600 #random.randint(200, 700)
OB_1_SCALE = 1.0
OB_2_X = 800 #random.randint(200, 1000)
OB_2_Y = 300 #random.randint(200, 700)
OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='Single Boid Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

boidList = []
obList = []

# #BEGIN THE BRIAN SIMULATION
# start_scope()
# A = 2.5
# f = 10*Hz
# tau = 5*ms
# N = 2

# eqs =  '''
# dv/dt = (1-v)/tau : 1
# '''

# # TimedArray appears to take in as input an array of values then the time interval.
# G = NeuronGroup(N, eqs, threshold='v>1', reset='v=0', method='exact')
# M = StateMonitor(G, variables=True, record=True)
# S = Synapses(G, G, 'w : 0.25', on_pre='v_post += w')
# S.connect(i=0, j=1)


# t_recorded = arange(int(200*ms/10*ms))*10*ms
# I_recorded = TimedArray(A*math.sin(2*math.pi*f*t_recorded), dt=10*ms) #starting dummy value, a simple sin wave

# G.run_regularly('I = I_recorded', dt=100*ms)

##################################################################################################
##################################################################################################
# # Command neurons
# tau = 1 * ms
# taus = 1.001 * ms
# wex = 7
# winh = -2
# eqs_neuron = '''
# dv/dt = (x - v)/tau : 1
# dx/dt = (y - x)/taus : 1 # alpha currents
# dy/dt = -y/taus : 1
# '''
# actuators = NeuronGroup(9, model=eqs_neuron, threshold='v>1', reset='v=0',
#                       method='exact')
# synapses_ex = Synapses(legs, actuators, on_pre='y+=wex')
# synapses_ex.connect(j='i')
# synapses_inh = Synapses(legs, actuators, on_pre='y+=winh', delay=deltaI)
# synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')
# spikes = SpikeMonitor(actuators)

# run(duration, report='text')

# nspikes = spikes.count
# phi_est = imag(log(sum(nspikes * exp(gamma * 1j))))
# print("True angle (deg): %.2f" % (phi/degree))
# print("Estimated angle (deg): %.2f" % (phi_est/degree))
# rmax = amax(nspikes)/duration/Hz
# polar(concatenate((gamma, [gamma[0] + 2 * pi])),
#       concatenate((nspikes, [nspikes[0]])) / duration / Hz,
#       c='k')
# axvline(phi, ls='-', c='g')
# axvline(phi_est, ls='-', c='b')
# show()
##################################################################################################
##################################################################################################






def init():
    global boidList, obList#, oneBoid_NET
    
    #init boids
    b_x = random.randint(X_START - 50, X_START + 50)
    b_y = random.randint(Y_START - 50, Y_START + 50)

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

# #this function will update the I value, so now I need to define new_I as the TimedArray recording of the spikes of what just happened......argh
# @network_operation(dt=10*ms)
# def change_I():
#     global I_recorded
#     G.I = I_recorded #need to define new_I

# def navigateBoids(dt):
#     global boidList, obList, I_recorded
#     #so this function's job is to correctly orientate the heading of the boid
#     #core equation is no longer relevant, the point is now to use input from the neural network

#     #I can use a TimedArray to actually record some data and use it right, and runtime can be the update interval
#     #the challenge is going to be getting output that's relevant

    
#     for burd in boidList:
#         #weights for further calibration
#         WEIGHT_OPTIMAL = 0.001
#         WEIGHT_OBSTACLE = [0.0] * len(obList) #this will use the inverse
#         offset_x = [0.0] * len(obList)
#         offset_y = [0.0] * len(obList)
#         index = 0

#         driveCurrent = [] #okay, so this contains the currents that will go into a TimedArray that will update I_recorded
#         #this will act as feedback into the neural network, and will generate, if any, spikes
#         #that spike data will go into stateMonitor M, where I can use M.v to get the voltage of each and find when the spikes occured
#         #THEN, I need to use said spike data to correct the boid heading
#         #the much easier way would be to set up a way that both are always running, and a spike in one results in the change in heading immediately
#         #current methodology is doomed to failure as the timing will mess things up, I can't react to moment in time that already passed
#         #although maybe I could do it so that the boid just follows what will happen? No but then it's not real time reacting

#         #wait Spikemonitor is a thing
#         #spikemon detects spikes and records when they happen in .t, a time variable

#         #Oh ffs I'm being dumb
#         #what I can do is use synapses, the post synaptic neuron firing will be what I need to know and ....

#         #nope that doesn't work either......ARGH

#         for ob in obList:
#             b_x, b_y = burd.getPos()
#             #get the distance from the boid to the obstacle
#             boidToSquare = ob.shortestDistance(b_x, b_y)
#             if boidToSquare < (120*ob.getScale()):
#                 offset_x[index], offset_y[index] = ob.offsetVelocities(b_x, b_y)
#                 WEIGHT_OBSTACLE[index] = 1/((boidToSquare) ** 2)
#             else:
#                 offset_x[index], offset_y[index] = 0.0, 0.0
#                 WEIGHT_OBSTACLE[index] = 0.0
#             index += 1

#         print('weights(OP, OB, B): ' + str(WEIGHT_OPTIMAL) + '   ' + str(WEIGHT_OBSTACLE))

#         burd.setToOptimalHeading()
#         burd.correctVelocities(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE, offset_x, offset_y)
#         # I_recorded = TimedArray(driveCurrent, dt=10*ms)
#         #burd.run(dt)
    

def navigateBoids(dt):
    #SNN takes in input of distances
    global boidList, obList

    for burd in boidList:
        b_x, b_y = burd.getPos()
        driveCurrent = []
        for ob in obList:
            boidToSquare = ob.shortestDistance(b_x, b_y)
            angleToSquare = ob.angleFromBoidToObject(b_x, b_y)
        
        


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
    run(5*60*1000*ms)
    pyglet.clock.schedule_interval(update, 1)
    pyglet.app.run()
