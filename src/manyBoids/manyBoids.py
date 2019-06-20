import numpy, pyglet, time, random, time
from game import physicalObject, physicalWall, boid, resources, load, util
from pyglet.gl import *

#dimensions for window
WIDTH = 3000 #1200
HEIGHT = 1500 #900

#start and end coords, WIDTH-
X_START = 50
Y_START = 1450
X_GOAL = 2900
Y_GOAL = 100

#coords and dimensions for rectangular obstacle
OB_1_X = 600#600#400##300
OB_1_Y = 1200#450#600##650
OB_1_SCALE = 1.0
OB_2_X = 1000#750 #800
OB_2_Y = 1000#500 #250
OB_2_SCALE = 0.5
OB_3_X = 2000
OB_3_Y = 1000
OB_3_SCALE = 2.0
OB_4_X = 2500
OB_4_Y = 500
OB_4_SCALE = 1.0
OB_5_X = 1500
OB_5_Y = 600
OB_5_SCALE = 1.0
OB_6_X = 850
OB_6_Y = 750
OB_6_SCALE = 0.5
OB_7_X = 1250
OB_7_Y = 1000
OB_7_SCALE = 0.25
OB_8_X = 1900
OB_8_Y = 400
OB_8_SCALE = 0.5
OB_9_X = 1150
OB_9_Y = 500
OB_9_SCALE = 0.5

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

titleLabel = pyglet.text.Label(text='Multiple Boids Maze Navigation', x=WIDTH/2 -100, y=HEIGHT-50, batch=drawBatch)
goalLabel = pyglet.text.Label(text='[    ] <- goal', x=X_GOAL-3, y=Y_GOAL, batch=drawBatch)

obstacles=None
boidList = []
finished_boids = []
taken_files = 0

obList = []
eventStackSize = 0


def init():
    global obstacles, boidList, obList, eventStackSize
    # BOID_NUMBER = int(input('enter number of boids: '))
    # print(str(BOID_NUMBER))

    BOID_NUMBER = 6

    for i in range(2):
        for j in range(3):
            new_boid = boid.Boid(x=X_START + (i*50), y=Y_START - (j*50), batch=drawBatch)
            new_boid.setTarget(X_GOAL, Y_GOAL)
            boidList.append(new_boid)

    #init boids
    # i = 0
    # while i < BOID_NUMBER:
    #     b_x = random.randint(X_START - 50, X_START + 50)
    #     b_y = random.randint(Y_START - 50, Y_START + 50)
    #     new_boid = boid.Boid(x=b_x, y=b_y, batch=drawBatch)
    #     append = True
    #     for burd in boidList:
    #         if util.distance(new_boid.getPos(), burd.getPos()) < 30:
    #             append = False
    #     if append:
    #         new_boid.setTarget(X_GOAL, Y_GOAL)
    #         boidList.append(new_boid)
    #     else:
    #         i-=1
    #     i+=1

    #init obstacles
    square_1 = physicalWall.Square(x=OB_1_X, y=OB_1_Y, batch=drawBatch)
    square_1.setScale(OB_1_SCALE)
    square_2 = physicalWall.Square(x=OB_2_X, y=OB_2_Y, batch=drawBatch)
    square_2.setScale(OB_2_SCALE)
    square_3 = physicalWall.Square(x=OB_3_X, y=OB_3_Y, batch=drawBatch)
    square_3.setScale(OB_3_SCALE)
    square_4 = physicalWall.Square(x=OB_4_X, y=OB_4_Y, batch=drawBatch)
    square_4.setScale(OB_4_SCALE)
    square_5 = physicalWall.Square(x=OB_5_X, y=OB_5_Y, batch=drawBatch)
    square_5.setScale(OB_5_SCALE)    
    square_6 = physicalWall.Square(x=OB_6_X, y=OB_6_Y, batch=drawBatch)
    square_6.setScale(OB_6_SCALE)
    square_7 = physicalWall.Square(x=OB_7_X, y=OB_7_Y, batch=drawBatch)
    square_7.setScale(OB_7_SCALE)    
    square_8 = physicalWall.Square(x=OB_8_X, y=OB_8_Y, batch=drawBatch)
    square_8.setScale(OB_8_SCALE)    
    square_9 = physicalWall.Square(x=OB_9_X, y=OB_9_Y, batch=drawBatch)
    square_9.setScale(OB_9_SCALE)


    obList = [square_1, square_2, square_3, square_4, square_5, square_6, square_7, square_8, square_9]

@gameWindow.event
def on_draw():
    global finished_boids
    gameWindow.clear()
    if boidList == []:
        glBegin(GL_LINES)
        for f in finished_boids:
            coords = f.get_record()
            for i in range(len(coords)-1):
                x_0, y_0 = coords[i]
                x_1, y_1 = coords[i+1]
                glVertex2i(int(x_0), int(y_0))
                glVertex2i(int(x_1), int(y_1))
        glEnd()
        for ob in obList:
            ob.draw()
    else:
        drawBatch.draw()

def normalise(W_OP, W_OB_B):
    total = W_OP + sum(W_OB_B)
    W_OB_B = [w / total for w in W_OB_B]
    retList = [W_OP/total, W_OB_B]
    return retList

def navigateBoids():
    global boidList, obList
    for burd in boidList:
        #weights for further calibration
        WEIGHT_OPTIMAL = 0.001
        WEIGHT_OBSTACLE_BOID = [0.0] * (len(obList) + len(boidList))
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
                b_x, b_y = otherBurds.getPos()
                boidToBoid = burd.shortestDistance(b_x, b_y)
                if boidToBoid < 100*otherBurds.getScale():
                    offset_x[index], offset_y[index] = burd.offsetVelocities(b_x, b_y)
                    WEIGHT_OBSTACLE_BOID[index] = 1/((1.25*boidToBoid) ** 2)
                #do not consider if distance too short
                else:
                    offset_x[index], offset_y[index] = 0.0, 0.0
                    WEIGHT_OBSTACLE_BOID[index] = 0.0
                index += 1
            else:
                #do not take self into account
                offset_x[index], offset_y[index] = 0.0, 0.0
                WEIGHT_OBSTACLE_BOID[index] = 0.0
                index+=1

        WEIGHT_OPTIMAL, WEIGHT_OBSTACLE_BOID = normalise(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE_BOID)

        burd.setToOptimalHeading()
        burd.correctVelocities(WEIGHT_OPTIMAL, WEIGHT_OBSTACLE_BOID, offset_x, offset_y)

def checkGoal():
    global finished_boids, boidList, taken_files
    for burd in boidList:
        b_x, b_y = burd.getPos()
        if X_GOAL-20 <=b_x <= X_GOAL+20 and Y_GOAL-20 <=b_y <= Y_GOAL+20:
            # TO SAVE DATA UN COMMENT THE LOWER NEXT LINE
            # burd.text_record_coords(str(FILENAME))
            boidList.remove(burd)
            finished_boids.append(burd)
            taken_files += 1 

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
    checkGoal()
    navigateBoids()

    for obj in gameList:
        obj.update(dt)


if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 0.08)
    pyglet.app.run()
