#Class inheriting from physcialObject.py
from game import physicalObject as phy
import pyglet, math, random, numpy
from game import resources, util

class Boid(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.scale = 0.5
        self.heading = -math.pi/4# * random.randint(0, 10)/10#start value
        self.rotation = -math.degrees(self.heading)
        self.target_x = 0
        self.target_y = 0
        self.resV = 30.0
        self.velocity_x = self.resV * math.cos(self.heading)
        self.velocity_y = self.resV * math.sin(self.heading)
        self.coord_record = [[self.x, self.y]]
    
    def setTarget(self, x, y):
        self.target_x = x
        self.target_y = y

    def correctVelocities(self, OP_weight, OB_B_weight, offset_x, offset_y):
        v_x, v_y = 0.0, 0.0

        offsetTotal_x = 0.0
        offsetTotal_y = 0.0
        for i in range(len(OB_B_weight)):
            offsetTotal_x += OB_B_weight[i] * offset_x[i]
            offsetTotal_y += OB_B_weight[i] * offset_y[i]

        v_x = (OP_weight * self.velocity_x) + offsetTotal_x
        v_y = (OP_weight * self.velocity_y) + offsetTotal_y

        newAngle = math.atan2(v_y, v_x)
        if 0 <= newAngle:
            self.rotation = 360 - math.degrees(newAngle)
        else:
            self.rotation = -math.degrees(newAngle)
        
        self.velocity_x = self.resV * math.cos(newAngle)
        self.velocity_y = self.resV * math.sin(newAngle)

    def update(self, dt):
        super(Boid, self).update(dt)
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.coord_record.append([self.x, self.y])

    def setToOptimalHeading(self):
        #optimal orientation: 
        diff_x = self.x - self.target_x
        diff_y = self.y - self.target_y 
        angleToDest = math.atan2(diff_y,diff_x)

        #top
        if 0 <= angleToDest:
            bestHeading = -(math.pi - angleToDest)
        #bottom
        else:
            bestHeading = math.pi + angleToDest

        self.velocity_x = self.resV * math.cos(bestHeading)
        self.velocity_y = self.resV * math.sin(bestHeading)

    def getPos(self):
        return self.position

    def shortestDistance(self, boid_x, boid_y):
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
    
    def offsetVelocities(self, otherBoid_x, otherBoid_y):
        offsetVX, offsetVY = 0.0, 0.0
        repulsionSpeed = self.resV
        diff_x, diff_y = 0.0, 0.0

        if otherBoid_y > self.y + self.image.height/2*self.scale:
            diff_y = otherBoid_y - (self.y + self.image.height/2*self.scale)

        elif otherBoid_y < self.y - self.image.height/2*self.scale:
            diff_y = otherBoid_y - (self.y - self.image.height/2*self.scale)

        if otherBoid_x < self.x - self.image.width/2*self.scale:
            diff_x = otherBoid_x - (self.x - self.image.width/2*self.scale)

        elif otherBoid_x > self.x + self.image.width/2*self.scale:
            diff_x = otherBoid_x - (self.x + self.image.width/2*self.scale)

        #angle between the two boids
        perpAngle = math.atan2(diff_y, diff_x)
        #as the boid will be heading in a certain direction, we adjust for heading
        diffHeading = perpAngle - self.heading

        if abs(diffHeading) < 0.8*math.pi: #considered range
            offsetVX = -repulsionSpeed * math.cos(diffHeading)
            offsetVY = -repulsionSpeed * math.sin(diffHeading)

        return offsetVX, offsetVY
    
    def getScale(self):
        return self.scale
    
    def getHeading(self):
        return self.heading

    def text_record_coords(self, file_index):
        numpy.savetxt(file_index, self.coord_record, delimiter=' ', newline=' ')

    def get_record(self):
        return self.coord_record

