#Class defining a physical object
import pyglet
from . import util

class Physical(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs): #x_start, y_start
        super(Physical, self).__init__(*args, **kwargs)
        self.collision = False
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.eventHandler = []

    def update(self, dt):
        pass
            
    def collidesWith(self, otherObject):
        #Determine if this object collides with another
        # Calculate distance between object centers that would be a collision assuming square resources
        collisionDistance = self.image.width * 0.5 * self.scale + otherObject.image.width * 0.5 * otherObject.scale

        # Get distance using position tuples
        actualDistance = util.distance(self.position, otherObject.position)

        return (actualDistance <= collisionDistance)

    def handleCollisionWith(self, otherObject):
        self.collision = True
