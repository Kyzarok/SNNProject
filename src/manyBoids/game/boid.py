#Class inheriting from physcialObject.py
from game import physicalObject as phy
import pyglet, math, random
from game import resources, util

class Boid(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.scale = 0.5
        self.heading = -math.pi/2 * random.randint(0, 10)/10#start value, is in radians and works of off same right aiming heading as trig funcs
        self.rotation = -math.degrees(self.heading) #maybe replace the maths for heading later in degrees
        self.target_x = 1100
        self.target_y = 100
        self.resV = 30.0
        self.velocity_x = self.resV * math.cos(self.heading)
        self.velocity_y = self.resV * math.sin(self.heading)

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
        print('new angle: ' +str(newAngle))
        if 0 <= newAngle:
            self.rotation = 360 - math.degrees(newAngle)
        else:
            self.rotation = -math.degrees(newAngle)
        
        self.velocity_x = self.resV * math.cos(newAngle)
        self.velocity_y = self.resV * math.sin(newAngle)

    def update(self, dt):
        #mathematically correct update function
        super(Boid, self).update(dt)
        #in the asteroid example, on an arrow key press the boid would rotate
        #here, the rotation angle will depend on the weightings
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        #here will be where we update the velocity
        #heading correction has already occured

    def setToOptimalHeading(self):
        #optimal orientation: 
        diff_x = self.x - self.target_x
        diff_y = self.y - self.target_y 
        angleToDest = math.atan2(diff_y,diff_x)
        #print('angleToDest: ' + str(angleToDest))

        #top
        if 0 <= angleToDest:
            bestHeading = -(math.pi - angleToDest)
        #bottom
        else:
            bestHeading = math.pi + angleToDest

        self.velocity_x = self.resV * math.cos(bestHeading)
        self.velocity_y = self.resV * math.sin(bestHeading)
        print('best heading is: ' + str(bestHeading))

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

        print('diffHeading: ' + str(diffHeading))
        if abs(diffHeading) < 0.8*math.pi: #considered range
            offsetVX = -repulsionSpeed * math.cos(diffHeading)
            offsetVY = -repulsionSpeed * math.sin(diffHeading)

        return offsetVX, offsetVY
    
    def getScale(self):
        return self.scale
    
    def getHeading(self):
        return self.heading