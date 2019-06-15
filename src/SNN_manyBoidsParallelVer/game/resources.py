import pyglet

def centerImage(image):
    #Sets an image's anchor point to its centerß
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2

# Tell pyglet where to find the resources
pyglet.resource.path = ['/Users/kai/Documents/SNNProject/src/SNN_oneBoid/']
pyglet.resource.reindex()

# Load the resources
boidImage = pyglet.resource.image("boid.png")
centerImage(boidImage)

squareImage = pyglet.resource.image("square.png")
centerImage(squareImage)
