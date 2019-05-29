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

#weights for further calibration
WEIGHT_OPTIMAL = 0.8 #temporary, most likely 1 minus the other two weights
WEIGHT_OBSTACLE = 0.1 #this will use the inverse 
WEIGHT_BOID = 0.1
#the boids will only take the effort to avoid the boid nearest to it

#coords and dimensions for rectangular obstacle
numOfObs = 1
OB_X = 450
OB_Y = 450
OB_WIDTH = 300
OB_HEIGHT = 300

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

#this can easily not be a global dude fix it
boidStillFlying = True

drawBatch = pyglet.graphics.Batch()

titleLabel = pyglet.text.Label(text='Single Boid Collision Avoidance', x=WIDTH/2, y=HEIGHT-50, batch=drawBatch)

aBoid=None
objList = []
eventStackSize = 0

def init():
    global aBoid, objList, eventStackSize
    #map initialised with zeroes
    #if object is in that space, not zero
    #if 1, it is wall
    #if 2, it is a boid
    coordMap = numpy.zeros((WIDTH, HEIGHT))
    
    #init obstacle
    #box = physicalWall.Square(x=OB_X, y=OB_Y)   # OB_WIDTH, OB_HEIGHT
    #if dimensions fit window, include obstacle in virtual map
    if (OB_X+OB_WIDTH/2<=WIDTH) and (OB_X-OB_WIDTH/2>=0) and (OB_Y+OB_HEIGHT/2<=HEIGHT) and (OB_Y-OB_HEIGHT>=0):
        for i in range (OB_X - int(OB_WIDTH/2), OB_X + int(OB_WIDTH/2)):
            for j in range (OB_Y - int(OB_HEIGHT/2), OB_Y + int(OB_HEIGHT/2)):
                coordMap[i][j] = 1
    
    #init boid sprite
    aBoid = boid.Boid(x=X_START, y=Y_START, batch=drawBatch) #X_GOAL, Y_GOAL, 

    #init obstacles
    #FILL THIS WITH A CONSTRUCTOR
    Obstacles = load.makeSquare(1, aBoid.position, drawBatch, WIDTH, HEIGHT)
    
    objList = [aBoid] + Obstacles

    for obj in objList:
        for handler in obj.eventHandler:
            gameWindow.push_handlers(handler)
            eventStackSize += 1
    

@gameWindow.event
def on_draw():
    gameWindow.clear()
    drawBatch.draw()

def navigateBoid(thisBoid):
    #so this function's job is to correctly orientate the heading of the boid
    #the core equation needs to account for other obstacles as well as opitmal heading
    heading = (WEIGHT_OPTIMAL * thisBoid.optimalHeading()) + (WEIGHT_OBSTACLE * 0) + (WEIGHT_BOID * 0) 
    thisBoid.setHandR(heading)
    
def update(dt):
    global objList
    for i in range(len(objList)):
        for j in range(i+1, len(objList)):
            obj_1 = objList[i]
            obj_2 = objList[j]
        if not obj_1.collision and not obj_2.collision:
            if obj_1.collidesWith(obj_2):
                obj_1.handleCollisionWith(obj_2)
                obj_2.handleCollisionWith(obj_1)

    for obj in objList:
        obj.update(dt)

    #need to draw the obstacles as well
 
    #so, first step
    #at this stage we're first trying to create the interactive environment
    #to do this we're gonna need to ignore the SNN stuff, and make the map
    #having tested both pygame and arcade, we're going with pyglet as it requires no other dependencies

    #right then, the game world is just a display, the window displays what's happening in the maps
    #this is good, I was worried that pixels would complicate the maths and I wouldn't be able to do any actual mathematics
    #however, because the display is an approximation of the maths, I can use all the vector maths I need to get the angles and values I need
    #so what's happening and what's displayed won't be 100% exact, but honestly it'll be too slight to tell]

    #considering the case of one boid, navigating around the world

    #we need a map to navigate in

    #we need a boid to navigate that map
    #here we'll make it start at point 0,0
    #ace = boid.Boid(0, 0)
    
    #we need an 'event loop' to do everything in, and an exit condition

    #TEST1: Make the boid move across the screen
    #while(boidStillFlying):
    #    navigateBoid()

if __name__ == '__main__':
    init()
    pyglet.clock.schedule_interval(update, 1/120)
    pyglet.app.run()
