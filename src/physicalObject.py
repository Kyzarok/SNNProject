#Class defining a physical object
import pyglet
import math

class Physical(pyglet.sprite.Sprite):

    def __init__(self, x_start, y_start):
        self.collision = False
        self.x = x_start
        self.y = y_start

    def collidesWith(self, otherObject):
        collision_distance = 
        actual_distance = self.distance(self.position, other_object.position)
        return (actual_distance <= collision_distance)

    def checkBounds(self):
        min_x = -self.image.width / 2
        min_y = -self.image.height / 2
        max_x = self.image.width / 2
        max_y = self.image.height / 2
        if self.x >= max_x | self.x <= min_x | self.y >= max_y | self.y <= min_y:
            raise Exception('Boid went out of bounds')
            exit()
