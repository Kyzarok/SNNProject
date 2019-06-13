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
    util.setGameObjects(boidList, obList)

@gameWindow.event
def on_draw():
    gameWindow.clear()
    drawBatch.draw()

def navigateBoid(actuator_spikes):
    global boidList
    for burd in boidList:
        burd.num_response(actuator_spikes)

    
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
    dt = 0.08
    actuator_spikes = util.receiveSpikes()
    navigateBoid(actuator_spikes)

    for obj in gameList:
        obj.update(dt)
    
    util.setGameObjects(boidList, obList)

if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 1)
    pyglet.app.run()