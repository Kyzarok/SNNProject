import pyglet, random
from game import physicalWall, resources

def makeSquare(self, numOfObs, boidPos, batch, width, height):
    obstacles = []
    for i in range(numOfObs):
        ob_x = width - 500
        ob_y = height - 400
        newOb = physicalWall.Square(x=ob_x, y=ob_y, batch=batch)
        newOb.rotation = random.randint(0, 360)
        newOb.velocity_x, newOb.velocity_y = 0.0, 0.0
        obstacles.append(newOb)
    return obstacles
