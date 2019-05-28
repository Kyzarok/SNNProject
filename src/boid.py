#Class inheriting from physcialObject.py
import physicalObject as phy
import math

class Boid(phy.Physical):

    def __init__(self, x_start, y_start, x_target, y_target):
        phy.Physical.__init__(self, x_start, y_start)
        self.heading = -math.pi/4 #start value, maybe randomize, is in radians and works of off same right aiming heading as trig funcs
        self.target_x = x_target
        self.target_y = y_target

    def update(self, dt):
        #mathematically correct update function
        self.x += 
        self.y += 
    
    def optimalHeading(self):
        #optimal orientation: 
        diff_x = self.target_x - self.x
        diff_y = self.target_y - self.y
        angleToDest = math.atan2(diff_y,diff_x)
        #literally just need to set this as the new bearing after some correction
        if 0 <= angleToDest <= math.pi/2:
            bestHeading = angleToDest - math.pi #checked
        elif angleToDest > math.pi/2:
            bestHeading = math.pi - angleToDest #checked
        elif -math.pi/2 <= angleToDest < 0:
            bestHeading = math.pi + angleToDest
        else: #angleToDest < -math.pi/2
            bestHeading = math.pi + angleToDest
        
        return bestHeading

    def setHeading(self, H):
        self.heading = H
