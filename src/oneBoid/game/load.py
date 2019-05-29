import pyglet, random
from game import physicalWall, resources

def makeSquare(numOfObs, boidPos, batch, width, height):
    obstacles = []
    for i in range(numOfObs):
        ob_x, ob_y = boidPos
        ob_x += 500
        ob_y -= 400
        newOb = physicalWall.Square(x=ob_x, y=ob_y, batch=batch)
        newOb.rotation = random.randint(0, 360)
        newOb.velocity_x, newOb.velocity_y = 0.0, 0.0
        obstacles.append(newOb)
    return obstacles
