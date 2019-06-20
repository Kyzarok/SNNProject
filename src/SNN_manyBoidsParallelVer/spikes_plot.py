import matplotlib.pyplot as plt
import numpy as np
from brian2 import *

index = 0
for i in range(6):
    big_array = []
    fname = 'spikes_' + str(index) + '.npy'
    big_array = np.load(fname)
    y_0 = []
    y_1 = []
    y_2 = []
    y_3 = []
    y_4 = []
    y_5 = []
    y_6 = []
    y_7 = []
    y_8 = []
    y_9 = []
    y_10 = []

    time = np.arange(len(big_array)) * (0.08*ms)
    for val in big_array:
        y_0.append(val[0])
        y_1.append(val[1])
        y_2.append(val[2])
        y_3.append(val[3])
        y_4.append(val[4])
        y_5.append(val[5])
        y_6.append(val[6])
        y_7.append(val[7])
        y_8.append(val[8])
        y_9.append(val[9])
        y_10.append(val[10])

    plt.plot(time, y_0)
    plt.plot(time, y_1)
    plt.plot(time, y_2)
    plt.plot(time, y_3)
    plt.plot(time, y_4)
    plt.plot(time, y_5)
    plt.plot(time, y_6)
    plt.plot(time, y_7)
    plt.plot(time, y_8)
    plt.plot(time, y_9)
    plt.plot(time, y_10)
    print('boid '+str(index))
    plt.show()
    index += 1
