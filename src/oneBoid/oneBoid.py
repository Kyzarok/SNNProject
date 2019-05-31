import numpy, pyglet, time
from game import physicalObject, physicalWall, boid, resources, load
from random import randint

#dimensions for window
WIDTH = 1200
HEIGHT = 900

#start and end coords
X_START = 100
Y_START = 800
X_GOAL = 1100
Y_GOAL = 100


#coords and dimensions for rectangular obstacle
numOfObs = 1
OB_1_X = 450
OB_1_Y = 600
OB_2_X = 700
OB_2_Y = 250


#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

#this can easily not be a global dude fix it
boidStillFlying = True

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='Single Boid Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL, y=Y_GOAL, batch=drawBatch)
mLabel = pyglet.text.Label(text='Maverick', x=X_START, y=Y_START, batch=drawBatch)
gLabel = pyglet.text.Label(text='Goose', x=X_START + 50, y=Y_START - 50, batch=drawBatch)

mBoid=None
gBoid=None
obstacles=None
boidList = []
obList = []
eventStackSize = 0


def init():
    global mBoid, gBoid, obstacles, boidList, obList, eventStackSize
    
    #init boid sprites
    maverick = boid.Boid(x=X_START, y=Y_START, batch=drawBatch) #X_GOAL, Y_GOAL, 
    goose = boid.Boid(x=X_START + 50, y=Y_START - 50, batch=drawBatch)

    #will need an initialiser that ensures they are far apart when they start

    #init obstacles
    square_1 = physicalWall.Square(x=OB_1_X, y=OB_1_Y, batch=drawBatch)
    square_1.setScale(1)
    square_2 = physicalWall.Square(x=OB_2_X, y=OB_2_Y, batch=drawBatch)
    square_2.setScale(0.5)
    
    #listed this way as later there will be a list of boids and it will be easier if we knew the index of the obstacles
    #or maybe I should just make two game object lists........ that's not a bad idea, could test boids on their own
    #yeah I'll do that - musings@19:06 30/05/2019
    obList = [square_1, square_2]
    boidList = [maverick, goose]

    #no event handlers necessary as no keyboard or mouse input

@gameWindow.event
def on_draw():
    # global mBoid, gBoid
    # m_x, m_y = mBoid.getPos()
    # g_x, g_y = gBoid.getPos()
    gameWindow.clear()
    # mLabel.x = m_x
    # mLabel.y = m_y
    # gLabel.x = g_x
    # gLabel.y = g_y
    drawBatch.draw()

def normalise(W_OP, W_OB, W_B):
    total = W_OP + sum(W_OB) + W_B
    W_OB = [w / total for w in W_OB]
    retList = [W_OP/total, W_OB, W_B/total]
    return retList

def navigateBoids():
    global boidList, obList
    #so this function's job is to correctly orientate the heading of the boid
    #the core equation needs to account for other obstacles as well as opitmal heading
    
    #nearestBoidHeading = 0

    #the boids will only take the effort to avoid the boid nearest to it
    
    for burd in boidList:
        #weights for further calibration
        WEIGHT_BOID = 0.0
        WEIGHT_OPTIMAL = 0.001
        WEIGHT_OBSTACLE = [0.0] * len(obList) #this will use the inverse
        offset_x = [0.0] * len(obList)
        offset_y = [0.0] * len(obList)
        index = 0
        for ob in obList:
            b_x, b_y = burd.getPos()
            #get the distance from the boid to the obstacle
            boidToSquare = ob.avoidance(b_x, b_y)
            if boidToSquare < 150:
                offset_x[index], offset_y[index] = ob.offsetVelocities(b_x, b_y)
                WEIGHT_OBSTACLE[index] = 1/((0.3*boidToSquare) ** 2)
            else:
                offset_x[index], offset_y[index] = 0.0, 0.0
                WEIGHT_OBSTACLE[index] = 0.0
            index += 1

        WEIGHT_OPTIMAL, WEIGHT_OBSTACLE, WEIGHT_BOID = normalise(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE, WEIGHT_BOID)
        print('weights(OP, OB, B): ' + str(WEIGHT_OPTIMAL) + '   ' + str(WEIGHT_OBSTACLE) + ' ' + str(WEIGHT_BOID))

        burd.setToOptimalHeading()
        burd.correctVelocities(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE, offset_x, offset_y)
    
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

    navigateBoids()

    for obj in gameList:
        obj.update(dt)

    #considering the case of one boid, navigating around the world
    
    #we need an 'event loop' to do everything in, and an exit condition

    #TEST1: Make the boid move across the screen
    #while(boidStillFlying):
    #    navigateBoid()

if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 1/4)
    pyglet.app.run()
