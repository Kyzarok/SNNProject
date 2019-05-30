import pyglet
from game import physicalWall, resources

def makeSquare(numOfObs, x, y, batch, width, height):
    obstacles = []
    for i in range(numOfObs):
        ob_x = x
        ob_y = y
        newOb = physicalWall.Square(x=ob_x, y=ob_y, batch=batch)
        newOb.rotation = 0
        obstacles.append(newOb)
    return obstacles
