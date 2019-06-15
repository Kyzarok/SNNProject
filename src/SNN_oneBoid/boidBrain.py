from brian2 import *

class hackySolution(SpikeMonitor):
    def reset(self):
        self.count = [0]*11
