from brian import *
#import pygame


def minimalGame():
    #template base pygame
    pygame.init() #initialize module

    #loading and setting the logo
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    #will often need a function to erase the current state of the screen
    #we can do this by reprinting the background, then the new image on top
    #then update as earlier with pygame.display.flip()
    #there are superior methods, but before optimising this you should get the rest of it working


    screen = pygame.display.set_mode((240,180)) #create a surface on screen that has size 240 x 180
    running = True

    image = pygame.image.load("01_image.png")
    screen.blit(image, (50,50))
    pygame.display.flip() #KEY: this is the screen update function

    #main loop, assume the game runs in here
    while running:
        #this is the event handling, gets all events from the event queue
        for event in pygame.event.get():
            #only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                #change the value to False, exit loop
                running = False

    #eventually chose against pygame as this has many bugs, seldom updated
    #instead we will use arcade


def initMaze():
    #various libraries I could use for this but the problem comes down to physics
    #if I do this by simple pixel grid 2D arrary trash this isn't going to be impressive
    #there'll be a way around this I'm sure, maybe there's a physics simulator library somewhere
    return 0

def initNodeBot():
    #this can be thought of as a singular boid
    #in future this function should create several boids
    #when this is done I will need to create some form of boid avoidance program
    #in "Not Bumping Into Things" and "Boids", there are specific principles and protocols in place, these were called steering behaviours
    #Separation, Collision Avoidance - steer to avoid crowding local flockmates
    #Alignment, Velocity matching - steer towards the average heading of local flockmates
    #Cohesion, Flock Centering - steer to move toward the average position of local flockmates
    #a critical detail is that each boid is not aware of the position and heading of every other boid, as they only needs to react to the ones in the near vicinity
    #in "boids", this vicinity was described as a wide arc around the area of the boid's heading.
    #the good news is that much of the maths was sorted out in 1987 and takes into account 3D whereas I don't have to
    #there is no bad news :P
    return 0

def createNet():
    #this'll be where the brian simulation is initialised
    return 0

def coreFunction() :
    #so, what do I need
    #if the name of the game is maze navigation I'm gonna need some form of display
    #Python should have some library somewhere that makes that easy enough
    #Maze randomization can be something to consider later
    #I need to make a maze, let's face it I can play around with a 2D arrary
    #Then single bot is the first step, looking at various papers it looks like operating on a neural net isn't unheard of
    #Once that's set up I'll need to link the Brian simulation to the actual bots inputs and outputs
    #Then I need to do some smart navigation stuff, hopefully the boids data will come in handy

    initMaze()
    initNodeBot()
    createNet()
