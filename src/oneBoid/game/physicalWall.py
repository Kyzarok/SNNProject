#Class inheriting from physicalObject
from game import physicalObject as phy
from game import resources, util
import math

class Square(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, batch
        super(Square, self).__init__(img=resources.obImage, *args, **kwargs)

    def update(self, dt):
        super(Square, self).update(dt)
        
    def avoidance(self, boid_x, boid_y):
        #circle around point, will need to do this for each point around the actual surface
        #calculate distance of point from each wall, find shortest one
        shortestDistance = 0.0
        # | a1 | a2 | a3 |
        # | b1 | NA | b3 |
        # | c1 | c2 | c3 |

        if self.x - self.image.width/2 <= boid_x < self.x + self.image.width/2:
            #a2
            if boid_y > self.y+self.image.height/2:
                shortestDistance = boid_y - (self.image.height/2 + self.y)
            #c2
            else:
                shortestDistance = (self.y - self.image.height/2) - boid_y
        #a1, b1, c1
        elif boid_x < self.x - self.image.width/2:
            #a1
            if boid_y > self.y + self.image.height/2:
                shortestDistance = util.distance((boid_x, boid_y),(self.x - self.image.width/2, self.y + self.image.height/2))
            #b1
            elif self.y - self.image.height/2 <= boid_y <= self.y + self.image.height/2:
                shortestDistance = self.x - self.image.width/2 - boid_x
            #c1
            else:
                shortestDistance = util.distance((boid_x, boid_y),(self.x - self.image.width/2, self.y - self.image.height/2))
        #a3, b3, c3
        else:
            #a3
            if boid_y > self.y + self.image.height/2:
                shortestDistance = util.distance((boid_x, boid_y),(self.x + self.image.width/2, self.y + self.image.height/2))
            #b3
            elif self.y - self.image.height/2 <= boid_y <= self.y + self.image.height/2:
                shortestDistance = boid_x - (self.x + self.image.width/2)
            #c3
            else:
                shortestDistance = util.distance((boid_x, boid_y),(self.x + self.image.width/2, self.y - self.image.height/2))

        return shortestDistance
    
    def offsetVelocities(self, boid_x, boid_y):
        offsetVX, offsetVY = 0.0, 0.0
        repulsionSpeed = 5.0
        #line function
        m = self.image.height/self.image.width
        cpos = self.y - m*self.x
        cneg = self.y + m*self.x

        if (boid_y > self.y + self.image.height/2) and (boid_y > (m*boid_x) + cpos) and (boid_y > (-m*boid_x) + cneg):
            offsetVX = -repulsionSpeed
            offsetVY = repulsionSpeed
        elif (boid_y < self.y - self.image.height/2) and (boid_y < (m*boid_x) + cpos) and (boid_y < (-m*boid_x) + cneg):
            offsetVX = repulsionSpeed
            offsetVY = -repulsionSpeed
        elif boid_x < self.x - self.image.width/2:
            offsetVX = -repulsionSpeed
            offsetVY = -repulsionSpeed
        elif boid_x > self.x + self.image.width/2:
            offsetVX = -repulsionSpeed
            offsetVY = -repulsionSpeed
        else:
            print('touching or inside SQUARE')

        return offsetVX, offsetVY


    def handleCollisionWith(self, otherObject):
        super(Square, self).handleCollisionWith(otherObject)
    
