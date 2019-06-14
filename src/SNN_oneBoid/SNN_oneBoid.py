import numpy, pyglet, time, random, boidBrain
from game import physicalObject, physicalWall, boid, resources, load, util
from brian2 import *
from multiprocessing import Process, Pipe
from functools import wraps

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

def navigateBoid(actuator_spikes):
    global boidList
    for burd in boidList:
        burd.num_response(actuator_spikes)

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
    
def update(dt, network_conn, physics_conn):
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
    dt = 0.08

    #receive spikes from network

    print('got to here')
    actuator_spikes_count = physics_conn.recv()
    print('received spikes')

    navigateBoid(actuator_spikes_count)

    for obj in gameList:
        obj.update(dt)
    
    physics_conn.send(updateInput(dt))
    print('sent updated input')

def RUN_PHYSICS(network_conn, physics_conn):
    pyglet.clock.schedule_interval(update, 1, network_conn, physics_conn)
    pyglet.app.run()

if __name__ == '__main__':
    init()
    network_conn, physics_conn = Pipe()
    print('SETTING PHYSICS')
    #dummy send for first iteration
    network_conn.send(None)
    p_1 = Process(target=RUN_PHYSICS, args=(network_conn, physics_conn,))
    print('SETTING NETWORK')
    p_2 = Process(target=boidBrain.RUN_NET, args=(physics_conn, network_conn,))
    print('STARTING PHYSICS')
    p_1.start()
    p_1.join()
    print('STARTING NETWORK')
    p_2.start()
    p_2.join()
