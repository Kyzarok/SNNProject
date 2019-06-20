from game import physicalObject as phy
import pyglet, math, random, numpy
from game import resources, util
from brian2 import *
from multiprocessing import Process, Pipe
import re


class Boid(phy.Physical):

    def __init__(self, *args, **kwargs):
        super(Boid, self).__init__(img=resources.boidImage, *args, **kwargs)
        self.scale = 0.5
        self.heading = -math.pi/4
        self.rotation = -math.degrees(self.heading)
        self.target_x = 0
        self.target_y = 0
        self.resV = 30.0
        self.velocity_x = self.resV * math.cos(self.heading)
        self.velocity_y = self.resV * math.sin(self.heading)
        self.old_spikes = [0] * 11
        self.coord_record = [[self.x, self.y]]
        self.spike_record = []
        self.flip_count = 0

    def setTarget(self, x, y):
        self.target_x = x
        self.target_y = y

    def update(self, dt):
        super(Boid, self).update(dt)

        self.velocity_x = self.resV * math.cos(self.heading)
        self.velocity_y = self.resV * math.sin(self.heading)
        if self.heading >= 0:
            self.rotation = 360 - math.degrees(self.heading)
        else:
            self.rotation = -math.degrees(self.heading)
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.coord_record.append([self.x, self.y])

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

    def num_response(self, actuator_spikes_literal):
        if(actuator_spikes_literal == None):
            print('NoneType Error')
        else:
            if self.flip_count > 3:
                self.flip()
                self.flip_count = 0

            else:
                l_bracket_position = actuator_spikes_literal.find('[')
                r_bracket_position = actuator_spikes_literal.find(']')

                res = actuator_spikes_literal[l_bracket_position + 1 : r_bracket_position]

                actuator_spikes = []
                for i in range(10):
                    index = res.find(',')
                    if index:
                        actuator_spikes.append(int(res[:index]))
                        res = res[index + 1:]
                actuator_spikes.append(int(res))

                new_spikes = actuator_spikes[:]

                for i in range(11):
                    new_spikes[i] -= self.old_spikes[i]
                self.spike_record.append(new_spikes)
                
                self.old_spikes = actuator_spikes[:]

                print('Spikes of sensors from most negative (-150 degrees) to most positive (+150 degrees) with the front of the boid being 0 degrees: ')
                print(new_spikes)

                new_heading = self.heading

                total = sum(new_spikes)
                if total == 0:
                    total = 1
                normalised = [x/total for x in new_spikes]

                for j in range(1, len(normalised)-1):
                    if j==1 or j==9:
                        normalised[j] *= 0.2
                    if j==2 or j==3 or j==7 or j==8:
                        normalised[j] *= 0.4
                    if j==4 or j==6:
                        normalised[j] *= 0.8


                for i in range(1, len(normalised)-1):
                    orientation = (-5*math.pi/6) + (i*math.pi/6)
                    new_heading += normalised[i] * orientation
                
                if (normalised[0] > 0.1) and (normalised[10] > 0.1):
                    new_heading += (normalised[0] + normalised[10])*(math.pi)
                else:
                    new_heading += (0.2*normalised[0] * (-5*math.pi/6)) + (0.2*normalised[10] * (5*math.pi/6))

                if new_heading > math.pi:
                    new_heading += -2*math.pi
                elif new_heading < -math.pi:
                    new_heading += 2*math.pi

                self.heading = new_heading
                position = self.getPos()

                print('BOID AT ' + str(position) + ' HAS NEW HEADING: ')
                print(self.heading)


    def avoid_sensor_input(self, dt, angle, weight, typeList):
        time = arange(int(dt / (1.0*ms)) + 1) * (1.0*ms)

        b_weight_factor = 10**4 * 0.45#0.4
        w_weight_factor = 10**4 * 1.5
        A_weight = [0] * 11
        frequency = [1.0] * 11

        for a in range(len(angle)): #go through the list of obstacles
            for i in range(10): #go through each sensor gap
                current_sensor_orientation = -5*math.pi/6 + i*math.pi/6 + self.heading
                diff = (-5*math.pi/6 + (i+1)*math.pi/6 + self.heading) - angle[a]

                if current_sensor_orientation > math.pi:
                    current_sensor_orientation += -2*math.pi
                elif current_sensor_orientation < -2*math.pi:
                    current_sensor_orientation += 2*math.pi

                if current_sensor_orientation <= angle[a] < current_sensor_orientation + math.pi/6:
                    weight_factor = 0
                    if typeList[a] == 'w':
                        weight_factor = w_weight_factor
                    elif typeList[a] == 'b':
                        weight_factor = b_weight_factor
                    A_weight[i] = 10 * (abs(diff/(math.pi/6))) * weight[a] * weight_factor
                    A_weight[i+1] = 10 * ((1-abs(diff/(math.pi/6)))) * weight[a] * weight_factor

                    frequency[i] *= 10 * (abs(diff/(math.pi/6)))
                    frequency[i+1] *= 10 * ((1 - abs(diff/(math.pi/6))))
        A = 1.0
        I_values = []
        for t in time:
            new = [0.0] * 11
            for k in range(len(frequency)):
                new[k] = (A*A_weight[k])*math.cos(2 * math.pi * (frequency[k]) * t)
            I_values.append(new)
        return I_values


    def optimal_sensor_input(self, dt, optimal):
        time = arange(int(dt / (1.0*ms)) + 1) * (1.0*ms)

        A_weight = [0.0] * 11
        frequency = [0.0] * 11

        BACKWARDS = True

        for i in range(10): #go through each sensor gap
            current_sensor_orientation = -5*math.pi/6 + i*math.pi/6 + self.heading
            diff = (-5*math.pi/6 + (i+1)*math.pi/6 + self.heading) - optimal

            if current_sensor_orientation > math.pi:
                current_sensor_orientation += -2*math.pi
            elif current_sensor_orientation < -2*math.pi:
                current_sensor_orientation += 2*math.pi

            if current_sensor_orientation <= optimal < current_sensor_orientation + math.pi/6:
                BACKWARDS = False
                A_weight[i] = 10 * (abs(diff/(math.pi/6)))
                A_weight[i+1] = 10 * ((1-abs(diff/(math.pi/6))))
                frequency[i] = (diff/(math.pi/6)) * 10
                frequency[i+1] = (1-diff/(math.pi/6)) * 10


        I_values = []

        if BACKWARDS:
            self.flip_count += 1

        for t in time:
            new = [0.0] * 11
            for k in range(len(frequency)):
                new[k] = (A_weight[k])*math.cos(2 * math.pi * (frequency[k]) * t)
            I_values.append(new)
        return I_values
    
    def flip(self):
        print('flipcalled')
        if self.heading >=0:
            self.heading += -math.pi
        else:
            self.heading += math.pi

    def angleFromBoidToBoid(self, boid_x, boid_y):
        diff_x, diff_y = 0.0, 0.0

        if boid_y > self.y + self.image.height/2*self.scale:
            diff_y = boid_y - (self.y + self.image.height/2*self.scale)

        elif boid_y < self.y - self.image.height/2*self.scale:
            diff_y = boid_y - (self.y - self.image.height/2*self.scale)

        if boid_x < self.x - self.image.width/2*self.scale:
            diff_x = boid_x - (self.x - self.image.width/2*self.scale)

        elif boid_x > self.x + self.image.width/2*self.scale:
            diff_x = boid_x - (self.x + self.image.width/2*self.scale)

        diffAngle = math.atan2(diff_y, diff_x)

        return diffAngle

    def text_record_spikes(self, file_index):
        fname = 'spikes_' + str(file_index)
        numpy.save(fname, self.spike_record)
    
    def text_record_coords(self, file_index):
        fname = 'coords_' + str(file_index)
        numpy.save(fname, self.coord_record)

    def get_record(self):
        return self.coord_record

