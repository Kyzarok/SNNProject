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
        avoidanceHeading = 0.0
        # | a1 | a2 | a3 |
        # | b1 | NA | b3 |
        # | c1 | c2 | c3 |

        #line function
        m = -(self.image.height/self.image.width)
        c = self.y - m*self.x

        if self.x - self.image.width/2 <= boid_x < self.x + self.image.width/2:
            #a2
            if boid_y > self.y+self.image.height/2:
                shortestDistance = boid_y - (self.image.height/2 + self.y)
                avoidanceHeading = 0.0
            #c2
            else:
                shortestDistance = (self.y - self.image.height/2) - boid_y
                avoidanceHeading = 0.0
        #a1, b1, c1
        elif boid_x < self.x - self.image.width/2:
            #a1
            if boid_y > self.y + self.image.height/2:
                shortestDistance = util.distance((boid_x, boid_y),(self.x - self.image.width/2, self.y + self.image.height/2))
                if boid_y > m*boid_x + c:
                    avoidanceHeading = 0.0
                else:
                    avoidanceHeading = -math.pi/2
            #b1
            elif self.y - self.image.height/2 <= boid_y <= self.y + self.image.height/2:
                shortestDistance = self.x - self.image.width/2 - boid_x
                avoidanceHeading = -math.pi/2
            #c1
            else:
                shortestDistance = util.distance((boid_x, boid_y),(self.x - self.image.width/2, self.y - self.image.height/2))
                if boid_y < m*boid_x + c:
                    avoidanceHeading = 0.0
                else:
                    avoidanceHeading = -math.pi/2
        #a3, b3, c3
        else:
            #a3
            if boid_y > self.y + self.image.height/2:
                shortestDistance = util.distance((boid_x, boid_y),(self.x + self.image.width/2, self.y + self.image.height/2))
                if boid_y > m*boid_x + c:
                    avoidanceHeading = 0.0
                else:
                    avoidanceHeading = -math.pi/2
            #b3
            elif self.y - self.image.height/2 <= boid_y <= self.y + self.image.height/2:
                shortestDistance = boid_x - (self.x + self.image.width/2)
                avoidanceHeading = -math.pi/2
                #print('in b3')
            #c3
            else:
                shortestDistance = util.distance((boid_x, boid_y),(self.x + self.image.width/2, self.y - self.image.height/2))
                if boid_y < m*boid_x + c:
                    avoidanceHeading = 0.0
                else:
                    avoidanceHeading = -math.pi/2

        return shortestDistance, avoidanceHeading

    def handleCollisionWith(self, otherObject):
        super(Square, self).handleCollisionWith(otherObject)
    
