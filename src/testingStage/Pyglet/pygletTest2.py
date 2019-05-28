import pyglet

window = pyglet.window.Window()
image = pyglet.image.load('/Users/kai/Desktop/Screenshot 2019-05-10 at 17.17.28.png', file=None, decoder=None)

@window.event
def on_draw():
    window.clear()
    image.blit(5, 5)

pyglet.app.run()
