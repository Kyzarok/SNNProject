from game import physicalObject as phy
import pyglet, math, random, numpy
from game import resources, util
from brian2 import *

class Boid(phy.Physical):#, Leaky.boid_net):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.scale = 0.5
        self.heading = -math.pi/4 #* random.randint(0, 10)/10#start value, is in radians and works of off same right aiming heading as trig funcs
        self.rotation = -math.degrees(self.heading) #maybe replace the maths for heading later in degrees
        self.target_x = 1100
        self.target_y = 100
        self.resV = 10.0
        self.velocity_x = self.resV * math.cos(self.heading)
        self.velocity_y = self.resV * math.sin(self.heading)

    def update(self, dt):
        super(Boid, self).update(dt)

        self.velocity_x = self.resV * math.cos(self.heading)
        self.velocity_y = self.resV * math.sin(self.heading)
        #print('new angle: ' +str(newAngle))
        if self.heading >= 0:
            self.rotation = 360 - math.degrees(self.heading)
        else:
            self.rotation = -math.degrees(self.heading)
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

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
    
    def getScale(self):
        return self.scale

    def getOptimalHeading(self):
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
        return bestHeading

    def wall_response(self, indices, times, weight):
        #print('total number of spikes is: ' + str(len(indices)))
        spike_frequency = [0.] * 11
        for i in range(11):
            timings = []
            index = 0
            for j in indices:
                if i == j: #if desired sensor
                    timings.append(times[index])
                index += 1
            #we now have the various timings that a specific sensor spiked
            delta_timings = [0.] * (len(timings) - 1)
            for k in range(len(timings)-1):
                delta_timings[k] = timings[k+1] - timings[k]
            average_delta_t = sum(delta_timings)/len(delta_timings)
            if average_delta_t > 0:
                spike_frequency[i] = 1/average_delta_t
        print(spike_frequency)
        total = sum(spike_frequency)
        print(total)
        spike_weight = [x/total for x in spike_frequency]
        print(spike_weight)
        tmp = -5*math.pi/6
        for i in range(len(spike_weight)):
            print(tmp)
            tmp += spike_weight[i] * (i * math.pi/6)
        self.heading = tmp

    def drive_currents(self, dt, angle, weight):
        time = arange(int(dt / defaultclock.dt) + 1) * defaultclock.dt
        #30 degrees is math.pi/6
        spike_1 = 0
        spike_2 = 0
        for i in range(10):
            current_orientation = -5*math.pi/6 + i*math.pi/6
            if current_orientation <= angle < current_orientation + math.pi/6:
                spike_1 = i
                spike_2 = i+1
        #we know where its inbetween, now we need to get the weights, for the frequencies
        #the closer it is to the sensor, the greater the frequency

        diff = (-5*math.pi/6 + spike_2*math.pi/6) - angle #this value will always be positive as ( -5*math.pi/6 + spike_2*math.pi/6) will always be greater than angle
        spike_2_weight = diff/(math.pi/6)
        spike_1_weight = 1 - spike_2_weight
        A = 2
        f = weight*100*Hz
        list_1 = [A*math.cos(2 * math.pi * (spike_1_weight * f) * t) for t in time]
        list_2 = [A*math.cos(2 * math.pi * (spike_2_weight * f) * t) for t in time]
        I_values = []
        for j in range(len(time)):
            new = [0.0] * 11
            new[spike_1] = list_1[j]
            new[spike_2] = list_2[j]
            I_values.append(new)
        I_values = TimedArray(I_values, dt=defaultclock.dt)
        return I_values, time
