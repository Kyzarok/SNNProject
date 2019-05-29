#Class inheriting from physcialObject.py
from game import physicalObject as phy
import pyglet, math
from game import resources

class Boid(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        phy.Physical(x_start, y_start)
        self.heading = -math.pi/4 #start value, maybe randomize, is in radians and works of off same right aiming heading as trig funcs
        self.rotation = 135.0 #maybe replace the maths for heading later in degrees
        self.target_x = args[1]
        self.target_y = args[2]
        self.eventHandler =[]

    def update(self, dt):
        #mathematically correct update function
        super(Boid, self).update(dt)

        #in the asteroid example, on an arrow key press the boid would rotate
        #here, the rotation angle will depend on the weightings
        
        
        #here will be where we update the velocity
        #heading correction has already occured
    
    def optimalHeading(self):
        #optimal orientation: 
        diff_x = self.target_x - self.x
        diff_y = self.target_y - self.y
        angleToDest = math.atan2(diff_y,diff_x)

        #top right
        if 0 <= angleToDest <= math.pi/2:
            bestHeading = angleToDest - math.pi
        #top left
        elif angleToDest > math.pi/2:
            bestHeading = math.pi - angleToDest
        #bottom right
        elif -math.pi/2 <= angleToDest < 0:
            bestHeading = math.pi + angleToDest
        #bottom left
        else: #angleToDest < -math.pi/2
            bestHeading = math.pi + angleToDest
        
        return bestHeading

    def setHandR(self, H):
        self.heading = H
        #top right
        if 0 <= H <= math.pi/2:
            self.rotation = 90 - math.degrees(H)
        #top left
        elif H > math.pi/2:
            self.rotation = 450 - math.degrees(H)
        #bottom right
        elif -math.pi/2 <= math < 0:
            self.rotation = 90 - math.degrees(H)
        #bottom left
        else:  #H < -math.pi/2
            self.rotation = 90 - math.degrees(H)
