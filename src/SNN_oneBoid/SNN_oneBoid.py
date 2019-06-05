import numpy, pyglet, time, random
from game import physicalObject, physicalWall, boid, resources, load, util

#dimensions for window
WIDTH = 1200
HEIGHT = 900

#start and end coords, WIDTH-
X_START = 50
Y_START = 850
X_GOAL = 1100
Y_GOAL = 100

#coords and dimensions for rectangular obstacle
OB_1_X = random.randint(200, 1000)
OB_1_Y = random.randint(200, 700)
OB_1_SCALE = 1.0
OB_2_X = random.randint(200, 1000)
OB_2_Y = random.randint(200, 700)
OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='Single Boid Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

boidList = []
obList = []


def init():
    global obstacles, boidList, obList, oneBoid_NET
    
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

def navigateBoids(dt):
    global boidList, obList
    #so this function's job is to correctly orientate the heading of the boid
    #core equation is no longer relevant, the point is now to use input from the neural network

    #I can use a TimedArray to actually record some data and use it right, and runtime can be the update interval
    #the challenge is going to be getting output that's relevant

    
    for burd in boidList:
        #weights for further calibration
        WEIGHT_OPTIMAL = 0.001
        WEIGHT_OBSTACLE = [0.0] * len(obList) #this will use the inverse
        offset_x = [0.0] * len(obList)
        offset_y = [0.0] * len(obList)
        index = 0

        for ob in obList:
            b_x, b_y = burd.getPos()
            #get the distance from the boid to the obstacle
            boidToSquare = ob.shortestDistance(b_x, b_y)
            if boidToSquare < (120*ob.getScale()):
                offset_x[index], offset_y[index] = ob.offsetVelocities(b_x, b_y)
                WEIGHT_OBSTACLE[index] = 1/((boidToSquare) ** 2)
            else:
                offset_x[index], offset_y[index] = 0.0, 0.0
                WEIGHT_OBSTACLE[index] = 0.0
            index += 1

        print('weights(OP, OB, B): ' + str(WEIGHT_OPTIMAL) + '   ' + str(WEIGHT_OBSTACLE))

        burd.setToOptimalHeading()
        burd.correctVelocities(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE, offset_x, offset_y)

        burd.run(dt)
    
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

    navigateBoids(dt)

    for obj in gameList:
        obj.update(dt)


if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 1/30)
    pyglet.app.run()
