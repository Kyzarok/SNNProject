#Class inheriting from physcialObject.py
from game import physicalObject as phy
import pyglet, math
from game import resources

class Boid(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.scale = 0.5
        self.heading = -math.pi/4 #start value, maybe randomize, is in radians and works of off same right aiming heading as trig funcs
        self.rotation = 45.0 #maybe replace the maths for heading later in degrees
        self.target_x = 1100
        self.target_y = 100
        self.velocity_x = 5.0
        self.velocity_y = -5.0
        self.resV = (self.velocity_x**2) + (self.velocity_y**2)

    def sign(self, a):
        if a > 0:
            return 1
        elif a < 0:
            return -1
        else:
            return 0

    def correctVelocities(self, OP_weight, OB_weight, offset_x, offset_y):
        v_x, v_y = 0.0, 0.0
        v_x = (OP_weight * self.velocity_x) + (OB_weight * offset_x)
        v_y = (OP_weight * self.velocity_y) + (OB_weight * offset_y)

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
        #print('best heading is: ' + str(bestHeading))

        self.velocity_x = self.resV * math.cos(bestHeading)
        self.velocity_y = self.resV * math.sin(bestHeading)
        print('best heading is: ' + str(bestHeading))

    def getPos(self):
        return self.position

    #def avoidObstacle(self):
        