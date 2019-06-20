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

    



    fig, (ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10) = plt.subplots(11)

    ax0.plot(0, 0, time, y_0)
    ax1.plot(0, 1, time, y_1)
    ax2.plot(0, 2, time, y_2)
    ax3.plot(1, 0, time, y_3)
    ax4.plot(1, 1, time, y_4)
    ax5.plot(1, 2, time, y_5)
    ax6.plot(2, 0, time, y_6)
    ax7.plot(2, 1, time, y_7)
    ax8.plot(2, 2, time, y_8)
    ax9.plot(3, 0, time, y_9)
    ax10.plot(3, 1, time, y_10)

    ax0.set(ylabel='-150')
    ax1.set(ylabel='-120')
    ax2.set(ylabel='-90')
    ax3.set(ylabel='-60')
    ax4.set(ylabel='-30')
    ax5.set(ylabel='0')
    ax6.set(ylabel='30')
    ax7.set(ylabel='60')
    ax8.set(ylabel='90')
    ax9.set(ylabel='120')
    ax10.set(ylabel='150', xlabel='time(ms)')
    print('boid '+str(index))
    plt.show()
    index += 1
