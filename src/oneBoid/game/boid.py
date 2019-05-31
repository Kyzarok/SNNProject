#Class inheriting from physcialObject.py
from game import physicalObject as phy
import pyglet, math
from game import resources

class Boid(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.image.scale = 0.25
        self.heading = -math.pi/4 #start value, maybe randomize, is in radians and works of off same right aiming heading as trig funcs
        self.rotation = 45.0 #maybe replace the maths for heading later in degrees
        self.target_x = 1100
        self.target_y = 100
        self.velocity_x = 10.0
        self.velocity_y = -10.0
        self.resultantVelocity = 0.0

    def sign(self, a):
        if a > 0:
            return 1
        elif a < 0:
            return -1
        else:
            return 0

    def correctVelocities(self):
        super(Boid,self).correctVelocities()
        self.resultantVelocity = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        self.velocity_x = self.resultantVelocity * math.cos(self.heading)
        self.velocity_y = self.resultantVelocity * math.sin(self.heading)

    def update(self, dt):
        #mathematically correct update function
        super(Boid, self).update(dt)
        #in the asteroid example, on an arrow key press the boid would rotate
        #here, the rotation angle will depend on the weightings
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        #here will be where we update the velocity
        #heading correction has already occured

    def optimalHeading(self):
        #optimal orientation: 
        diff_x = self.x - self.target_x
        diff_y = self.y - self.target_y 
        angleToDest = math.atan2(diff_y,diff_x)
        print('angleToDest: ' + str(angleToDest))

        #top
        if 0 <= angleToDest:
            bestHeading = -(math.pi - angleToDest)
        #bottom
        else:
            bestHeading = math.pi + angleToDest
        print('best heading is: ' + str(bestHeading))
        return bestHeading

    def setHandR(self, H):
        self.heading = H
        #top
        if 0 <= H :
            self.rotation = 360 - math.degrees(H)
        #bottom
        else:  #H < 0
            self.rotation = - math.degrees(H)

    def getPos(self):
        return self.position

    #def avoidObstacle(self):
        