#Class inheriting from physicalObject
from game import physicalObject as phy
from game import resources, util
import math

class Square(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, batch
        super(Square, self).__init__(img=resources.squareImage, *args, **kwargs)

    def update(self, dt):
        super(Square, self).update(dt)
        
    def shortestDistance(self, boid_x, boid_y):
        #circle around point, will need to do this for each point around the actual surface
        #calculate distance of point from each wall, find shortest one
        shortestDistance = 0.0
        # | a1 | a2 | a3 |
        # | b1 | NA | b3 |
        # | c1 | c2 | c3 |

        if self.x - self.image.width/2*self.scale <= boid_x < self.x + self.image.width/2*self.scale:
            #a2
            if boid_y > self.y+self.image.height/2*self.scale :
                shortestDistance = boid_y - (self.image.height/2*self.scale + self.y)
            #c2
            else:
                shortestDistance = (self.y - self.image.height/2*self.scale ) - boid_y
        #a1, b1, c1
        elif boid_x < self.x - self.image.width/2*self.scale :
            #a1
            if boid_y > self.y + self.image.height/2*self.scale :
                shortestDistance = util.distance((boid_x, boid_y),(self.x - self.image.width/2*self.scale , self.y + self.image.height/2*self.scale ))
            #b1
            elif self.y - self.image.height/2*self.scale  <= boid_y <= self.y + self.image.height/2*self.scale :
                shortestDistance = self.x - self.image.width/2*self.scale  - boid_x
            #c1
            else:
                shortestDistance = util.distance((boid_x, boid_y),(self.x - self.image.width/2*self.scale , self.y - self.image.height/2*self.scale ))
        #a3, b3, c3
        else:
            #a3
            if boid_y > self.y + self.image.height/2*self.scale :
                shortestDistance = util.distance((boid_x, boid_y),(self.x + self.image.width/2*self.scale , self.y + self.image.height/2*self.scale ))
            #b3
            elif self.y - self.image.height/2*self.scale  <= boid_y <= self.y + self.image.height/2*self.scale :
                shortestDistance = boid_x - (self.x + self.image.width/2*self.scale )
            #c3
            else:
                shortestDistance = util.distance((boid_x, boid_y),(self.x + self.image.width/2*self.scale , self.y - self.image.height/2*self.scale ))

        return shortestDistance
    
    def offsetVelocities(self, boid_x, boid_y):
        offsetVX, offsetVY = 0.0, 0.0
        repulsionSpeed = 30.0
        diff_x, diff_y = 0.0, 0.0

        if boid_y > self.y + self.image.height/2*self.scale:
            diff_y = boid_y - (self.y + self.image.height/2*self.scale)

        elif boid_y < self.y - self.image.height/2*self.scale:
            diff_y = boid_y - (self.y - self.image.height/2*self.scale)

        if boid_x < self.x - self.image.width/2*self.scale:
            diff_x = boid_x - (self.x - self.image.width/2*self.scale)

        elif boid_x > self.x + self.image.width/2*self.scale:
            diff_x = boid_x - (self.x + self.image.width/2*self.scale)

        diffHeading = math.atan2(diff_y, diff_x)

        offsetVX = repulsionSpeed * math.cos(diffHeading)
        offsetVY = repulsionSpeed * math.sin(diffHeading)

        return offsetVX, offsetVY


    def handleCollisionWith(self, otherObject):
        super(Square, self).handleCollisionWith(otherObject)
    
    def setScale(self, scale):
        self.scale = scale
    
    def getScale(self):
        return self.scale
