import pyglet, math
boidList = []
obList = []
spikes = None

def distance(point_1=(0, 0), point_2=(0, 0)):
    #Returns the distance between two points
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)

def centerImage(image):
    #Sets an image's anchor point to its center
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2

def setGameObjects(bList, oList):
    global boidList, obList
    boidList = bList
    obList = oList

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


def sendSpikes(actuator_spikes):
    global spikes
    spikes = actuator_spikes

def receiveSpikes():
    global spikes
    return spikes