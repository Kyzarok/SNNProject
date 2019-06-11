from game import physicalObject as phy
import pyglet, math, random, numpy
from game import resources, util
from brian2 import *

class Boid(phy.Physical):#, Leaky.boid_net):

    def __init__(self, *args, **kwargs): #x_start, y_start, x_target, y_target
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.scale = 0.5
        self.heading = 0#-math.pi/4 #* random.randint(0, 10)/10#start value, is in radians and works of off same right aiming heading as trig funcs
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


    def getOptimalHeading(self):
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
        
        return bestHeading

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

    def response(self, actuator_spikes, weight):
        print("actuator_spikes.count: ")
        print(actuator_spikes.count)
        print("actuator_spikes.i: ")
        print(actuator_spikes.i)
        print("actuator_spikes.t: ")
        print(actuator_spikes.t)



        #BELOW IS BASED OFF OF FREQUENCIES
        # spike_frequency = [0.] * 11
        # for i in range(11):
        #     timings = []
        #     index = 0
        #     for j in indices:
        #         if i == j: #if desired sensors
        #             timings.append(times[index])
        #         index += 1
        #     #we now have the various timings that a specific sensor spiked
        #     delta_timings = [0.] * (len(timings) - 1)
        #     for k in range(len(timings)-1):
        #         delta_timings[k] = timings[k+1] - timings[k]
        #     average_delta_t = sum(delta_timings)/len(delta_timings)
        #     if average_delta_t > 0:
        #         spike_frequency[i] = 1/average_delta_t
        # # print("spike_frequency: ")
        # # print(spike_frequency)
        # total = sum(spike_frequency)
        # # print("total: ")
        # # print(total)
        # spike_weight = [x/total for x in spike_frequency]
        # print("spike_weight: ")
        # print(spike_weight)
        # tmp = -5*math.pi/6 + self.heading
        # for i in range(len(spike_weight)):
        #     tmp += spike_weight[i] * (i * math.pi/6)
        # if tmp < -math.pi:
        #     self.heading = tmp + 2*math.pi
        # elif tmp > math.pi:
        #     self.heading = -2*math.pi + tmp
        # else:
        #     self.heading = tmp
        # print(self.heading)



    #returns 2D TimedArray, called I_values
    #generates lower frequencies for directions it needs to avoid, and higher for those desired
    def drive_currents(self, dt, angle, weight, optimal):
        time = arange(int(dt / defaultclock.dt) + 1) * defaultclock.dt

        frequency = [50.0]*11
        distance_calibration = 150

        for a in range(len(angle)):
            for i in range(10):
                current_orientation = -5*math.pi/6 + i*math.pi/6 + self.heading
                if current_orientation <= angle[a] < current_orientation + math.pi/6:
                    diff = (-5*math.pi/6 + (i+1)*math.pi/6 + self.heading) - a
                    frequency[i] = ( 0.1 * frequency[i] * ( diff/(math.pi/6)) ) * (weight[a] / 150)
                    frequency[i+1] = ( 0.1 * frequency[i+1] * ( 1 - diff/math.pi/6) ) * (weight[a] / 150)
                    frequency[i] = 1.0
                    frequency[i+1] = 1.0
                
                if current_orientation <= optimal < current_orientation + math.pi/6:
                    diff = (-5*math.pi/6 + (i+1)*math.pi/6 + self.heading) - a
                    frequency[i] *= frequency[i] * (1+(diff/(math.pi/6))) * 10
                    frequency[i+1] *= frequency[i+1] * (1+(1-diff/(math.pi/6))) * 10

        A = 5
        I_values = []
        for t in time:
            new = [0.0] * 11
            for k in range(len(frequency)):
                new[k] = A*math.cos(2 * math.pi * (frequency[k]) * t)
            I_values.append(new)
        ret_values = TimedArray(I_values, dt=defaultclock.dt)
        return ret_values