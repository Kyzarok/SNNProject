#Class inheriting from physicalObject
from game import physicalObject as phy
from game import resources

class Square(phy.Physical):

    def __init__(self, *args, **kwargs): #x_start, y_start, batch
        super(Square, self).__init__(img=resources.obImage, *args, **kwargs)

    def update(self, dt):
        super(Square, self).update(dt)
        
    def fieldRange(self):
        #circle around point, will need to do this for each point around the actual surface
        pass

    def handleCollisionWith(self, otherObject):
        super(Square, self).handleCollisionWith(otherObject)
