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

titleLabel = pyglet.text.Label(text='Single Boid Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

boidList = []
obList = []

def init():
    global boidList, obList
    
    #init boids
    b_x = X_START #random.randint(X_START - 50, X_START + 50)
    b_y = Y_START #random.randint(Y_START - 50, Y_START + 50)

    maverick = boid_brain.SmartBoid(x=b_x, y=b_y, batch=drawBatch)

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
            sensor_input = burd.runSensors(angleToSquare, dt)
            weight = 1/(boidToSquare ** 2)
            burd.runAcutators(sensor_input, weight, dt)

            

    #actuatorSpikes = burd.run(driveCurrent, dt)



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
