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
        self.resV = 30.0
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
        #print("new_coords: " + str(self.x) + ' ' + str(self.y))

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

    def num_response(self, actuator_spikes, weight):
        print("actuator_spikes.count: ")
        print(actuator_spikes.count)

        new_heading = 0.0

        total = sum(actuator_spikes.count)
        normalised = [x/total for x in actuator_spikes.count]

        if normalised[0] > 0.1 and normalised [10] > 0.1:
            self.resV = 30.0 * (1 - normalised[0] - normalised[1])
        else:
            self.resV = 30.0

        for i in range(len(normalised)):
            new_heading += normalised[i] * ((-5*math.pi/6) + (i*math.pi/6))

        self.heading += new_heading

        if new_heading > math.pi:
            new_heading += -2*math.pi
        elif new_heading < -math.pi:
            new_heading += 2*math.pi

    def avoid_sensor_input(self, dt, angle, weight, typeList):
        time = arange(int(dt / (0.1*ms)) + 1) * (0.1*ms)

        BACKWARDS = True

        w_weight_bound = (1/(100**2)) * 1.5
        b_weight_bound = (1/50**2)
        A_weight = [0.0] * 11
        frequency = [1.0] * 11

        for a in range(len(angle)): #go through the list of obstacles
            for i in range(10): #go through each sensor
                current_sensor_orientation = -5*math.pi/6 + i*math.pi/6 + self.heading
                diff = (-5*math.pi/6 + (i+1)*math.pi/6 + self.heading) - angle[a]

                if current_sensor_orientation > math.pi:
                    current_sensor_orientation += -2*math.pi
                elif current_sensor_orientation < -2*math.pi:
                    current_sensor_orientation += 2*math.pi

                if current_sensor_orientation <= angle[a] < current_sensor_orientation + math.pi/6:

                    BACKWARDS = False
                    if typeList[a] == 'b':
                        weight_bound = b_weight_bound
                    else:
                        weight_bound = w_weight_bound
                    
                    A_weight[i] += (weight[a]/weight_bound)
                    A_weight[i+1] += (weight[a]/weight_bound)

                    frequency[i] *= 10 * (1+abs(diff/(math.pi/6)))
                    frequency[i+1] *= 10 * (1+(1 - abs(diff/(math.pi/6))))

        # if BACKWARDS:
        #     print('NEEDS_TO_FLIP_1')

        A = 1.0
        I_values = []
        for t in time:
            new = [0.0] * 11
            for k in range(len(frequency)):
                new[k] = (A*A_weight[k])*math.cos(2 * math.pi * (frequency[k]) * t)
            I_values.append(new)
        ret_values = TimedArray(I_values, 0.1*ms)
        return ret_values



    def optimal_sensor_input(self, dt, optimal):
        time = arange(int(dt / (0.1*ms)) + 1) * (0.1*ms)

        BACKWARDS = True

        A_weight = [0.0] * 11
        frequency = [0.0] * 11

        for i in range(10): #go through each sensor
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

        # if BACKWARDS:
        #     print('NEEDS_TO_FLIP_2')

        # print(A_weight)

        I_values = []
        for t in time:
            new = [0.0] * 11
            for k in range(len(frequency)):
                new[k] = (A_weight[k])*math.cos(2 * math.pi * (frequency[k]) * t)
            I_values.append(new)
        ret_values = TimedArray(I_values, 0.1*ms)
        return ret_values

    def angleFromBoidToBoid(self, boid_x, boid_y):
        #correct for heading, so +- pi
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

    def runBoidBrain(self, I_avoid, I_attract, dt):
        start_scope()

        # Parameters
        duration = dt
        deltaI = .7*ms  # inhibitory delay

        tau_sensors = 0.1*ms
        eqs_avoid = '''
        dv/dt = (I - v)/tau_sensors : 1
        I = I_avoid(t, i) : 1
        '''
        negative_sensors = NeuronGroup(11, model=eqs_avoid, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler')
        neg_spikes_sensors = SpikeMonitor(negative_sensors)
        

        eqs_attract= '''
        dv/dt = (I - v)/tau_sensors : 1
        I = I_attract(t, i) : 1
        '''
        positive_sensors = NeuronGroup(11, model=eqs_attract, threshold='v > 1.0', reset='v = 0', refractory=1*ms, method='euler')
        pos_spikes_sensors = SpikeMonitor(positive_sensors)

        # Command neurons
        tau = 1 * ms
        taus = 1.001 * ms
        wex = 5
        winh = -2
        eqs_actuator = '''
        dv/dt = (x - v)/tau : 1
        dx/dt = (y - x)/taus : 1 # alpha currents
        dy/dt = -y/taus : 1
        '''
        actuators = NeuronGroup(11, model=eqs_actuator, threshold='v>2', reset='v=0', method='exact')
        synapses_ex = Synapses(negative_sensors, actuators, on_pre='y+=winh')
        synapses_ex.connect(j='i')
        synapses_inh = Synapses(negative_sensors, actuators, on_pre='y+=wex', delay=deltaI)
        synapses_inh.connect('abs(((j - i) % N_post) - N_post/2) <= 1')

        WEXCITE = 7

        synapses_EXCITE = Synapses(positive_sensors, actuators, on_pre='y+=WEXCITE')
        synapses_EXCITE.connect(j='i')


        spikes = SpikeMonitor(actuators)

        run(duration)

        print("negative_sensors.count: ")
        print(neg_spikes_sensors.count)
        print("positive_sensors.count: ")
        print(pos_spikes_sensors.count)
        return spikes