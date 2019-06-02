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

    # def checkBounds(self):
    #     min_x = -self.image.width / 2
    #     min_y = -self.image.height / 2
    #     max_x = self.image.width / 2
    #     max_y = self.image.height / 2
    #     if self.x >= max_x or self.x <= min_x or self.y >= max_y or self.y <= min_y:
    #         raise Exception('Out of bounds')
    #         exit()

            
    def collidesWith(self, otherObject):
        #Determine if this object collides with another
        # Calculate distance between object centers that would be a collision assuming square resources
        collisionDistance = self.image.width * 0.5 * self.scale + otherObject.image.width * 0.5 * otherObject.scale

        # Get distance using position tuples
        actualDistance = util.distance(self.position, otherObject.position)

        return (actualDistance <= collisionDistance)

    def handleCollisionWith(self, otherObject):
        if otherObject.__class__ is not self.__class__:
            self.collision = True
