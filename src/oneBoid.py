import numpy
import pyglet
import boid
import physicalWall
from random import randint
import time

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
OB_X = 450
OB_Y = 450
OB_WIDTH = 300
OB_HEIGHT = 300


burd = boid.Boid(X_START, Y_START, X_GOAL, Y_GOAL)
navigateBoid(burd)

#define window height and width
gameWindow = pyglet.window.Window(width=WIDTH, height=HEIGHT)

#this can easily not be a global dude fix it
boidStillFlying = True

#pyglet.resource.path = ['/Users/kai/Documents/SNNProject']
#pyglet.resource.reindex()

#boid_image = ("boid.png")

boidSprite = pyglet.sprite.Sprite(img=pyglet.image.load('/Users/kai/Documents/SNNProject/src/boid.png'), x=400, y=300)
boidSprite.scale = 0.5

#def initMap():
    #the world map will be created here, complete with obstacles
    #I will create a 2D array representing a grid of items


#map initialised with zeroes
#if object is in that space, not zero
#if 1, it is wall
#if 2, it is a boid
coordMap = numpy.zeros((WIDTH, HEIGHT))
for i in range (300, 600):
    for j in range (300, 600):
        coordMap[i][j] = 1
        

drawBatch = pyglet.graphics.Batch()

#init obstacle
box = physicalWall.Rect(OB_X, OB_Y, OB_WIDTH, OB_HEIGHT)
#add obstacle
drawBatch.add(box.getVertexNum, pyglet.gl.GL_QUADS, None, ('v2i',box.getVertices), ('c4B',box.getColour*4))

titleLabel = pyglet.text.Label(text='Swarm Control', x=WIDTH/2, y=HEIGHT-50, batch=drawBatch)


#@gameWindow.event
#def on_key_press(symbol, modifiers):


@gameWindow.event
def on_draw():
    gameWindow.clear()
    titleLabel.draw()
    #boidSprite.draw()
    drawBatch.draw()

def pointToLine():
    pass
    #calculates the shortest distance between a line and a point

def navigateBoid(thisBoid):
    #so this function's job is to correctly orientate the heading of the boid
    #the core equation needs to account for other obstacles as well as opitmal heading
    heading = (WEIGHT_OPTIMAL * thisBoid.optimalHeading()) + (WEIGHT_OBSTACLE * 0) + (WEIGHT_BOID * 0) 
    thisBoid.setHeading(heading)
    

def update(dt):
    #for obj in gameObjects:
    burd.update(dt)

    
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
    pyglet.clock.schedule_interval(update, 1/120)
    pyglet.app.run()
