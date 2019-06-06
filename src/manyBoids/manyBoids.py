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
OB_1_X = 400 #random.randint(200, 1000)
OB_1_Y = 600 #random.randint(200, 700)
OB_1_SCALE = 1.0
OB_2_X = 800 #random.randint(200, 1000)
OB_2_Y = 250 #random.randint(200, 700)
OB_2_SCALE = 0.5

# #values for getting trapped
# OB_1_X = 500 
# OB_1_Y = 350 
# OB_1_SCALE = 1.0
# OB_2_X = 600 
# OB_2_Y = 500
# OB_2_SCALE = 0.5

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

#this can easily not be a global dude fix it
boidStillFlying = True

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='Multiple Boids Collision Avoidance', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)
#mLabel = pyglet.text.Label(text='Maverick', x=X_START, y=Y_START, batch=drawBatch)
#gLabel = pyglet.text.Label(text='Goose', x=X_START + 50, y=Y_START - 50, batch=drawBatch)

obstacles=None
boidList = []
obList = []
eventStackSize = 0


def init():
    global obstacles, boidList, obList, eventStackSize
    BOID_NUMBER = int(input('enter number of boids: '))
    print(str(BOID_NUMBER))
    
    #init boids
    i = 0
    while i < BOID_NUMBER:
        b_x = random.randint(X_START - 50, X_START + 50)
        b_y = random.randint(Y_START - 50, Y_START + 50)
        new_boid = boid.Boid(x=b_x, y=b_y, batch=drawBatch)
        append = True
        for burd in boidList:
            if util.distance(new_boid.getPos(), burd.getPos()) < 30:
                append = False
        if append:
            boidList.append(new_boid)
        else:
            i-=1
        i+=1

    #init obstacles
    square_1 = physicalWall.Square(x=OB_1_X, y=OB_1_Y, batch=drawBatch)
    square_1.setScale(OB_1_SCALE)
    square_2 = physicalWall.Square(x=OB_2_X, y=OB_2_Y, batch=drawBatch)
    square_2.setScale(OB_2_SCALE)
    
    #listed this way as later there will be a list of boids and it will be easier if we knew the index of the obstacles
    #or maybe I should just make two game object lists........ that's not a bad idea, could test boids on their own
    #yeah I'll do that - musings@19:06 30/05/2019
    obList = [square_1, square_2]
    # boidList = [nimbus, serenity, nirvash, blue_beetle, red_five, mehve]

    #no event handlers necessary as no keyboard or mouse input

@gameWindow.event
def on_draw():
    gameWindow.clear()
    drawBatch.draw()

def normalise(W_OP, W_OB_B):
    total = W_OP + sum(W_OB_B)
    W_OB_B = [w / total for w in W_OB_B]
    retList = [W_OP/total, W_OB_B]
    return retList

def navigateBoids():
    global boidList, obList
    #so this function's job is to correctly orientate the heading of the boid
    #the core equation needs to account for other obstacles as well as opitmal heading
    
    #nearestBoidHeading = 0

    #the boids will only take the effort to avoid the boid nearest to it
    
    for burd in boidList:
        #weights for further calibration
        WEIGHT_OPTIMAL = 0.001
        WEIGHT_OBSTACLE_BOID = [0.0] * (len(obList) + len(boidList)) #this will use the inverse
        offset_x = [0.0] * (len(obList) + len(boidList))
        offset_y = [0.0] * (len(obList) + len(boidList))
        index = 0

        for ob in obList:
            b_x, b_y = burd.getPos()
            #get the distance from the boid to the obstacle
            boidToSquare = ob.shortestDistance(b_x, b_y)
            if boidToSquare < (120*ob.getScale()):
                offset_x[index], offset_y[index] = ob.offsetVelocities(b_x, b_y)
                WEIGHT_OBSTACLE_BOID[index] = 1/((0.85*boidToSquare) ** 2)
            else:
                offset_x[index], offset_y[index] = 0.0, 0.0
                WEIGHT_OBSTACLE_BOID[index] = 0.0
            index += 1

        for otherBurds in boidList:
            if burd != otherBurds:
                #print('avoiding')
                b_x, b_y = otherBurds.getPos()
                boidToBoid = burd.shortestDistance(b_x, b_y)
                #print('distance between boids: ' + str(boidToBoid))
                if boidToBoid < 100*otherBurds.getScale():
                    offset_x[index], offset_y[index] = burd.offsetVelocities(b_x, b_y)
                    WEIGHT_OBSTACLE_BOID[index] = 1/((1.25*boidToBoid) ** 2)
                #do not consider if distance too short
                else:
                    offset_x[index], offset_y[index] = 0.0, 0.0
                    WEIGHT_OBSTACLE_BOID[index] = 0.0
                index += 1
                #print('value of index: ' + str(index))
            else:
                #do not take self into account
                offset_x[index], offset_y[index] = 0.0, 0.0
                WEIGHT_OBSTACLE_BOID[index] = 0.0
                index+=1

        WEIGHT_OPTIMAL, WEIGHT_OBSTACLE_BOID = normalise(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE_BOID)
        print('weights(OP, OB, B): ' + str(WEIGHT_OPTIMAL) + '   ' + str(WEIGHT_OBSTACLE_BOID))

        burd.setToOptimalHeading()
        burd.correctVelocities(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE_BOID, offset_x, offset_y)
    
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
    pyglet.clock.schedule_interval(update, 1/10)
    pyglet.app.run()
