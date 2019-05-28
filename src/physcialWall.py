#Class inheriting from physicalObject
import physicalObject as Phy

class Rect(phy.Physical):

    def __init__(self, x_start, y_start, width, height):
        phy.Physical.__init__(self, x_start, y_start)
        self.vertexNumber = 4
        self.vertexList = [x_start - width/2, y_start + height/2, x_start - width/2, y_start - height/2, x_start + width/2, y_start - height/2, x_start + width/2, y_start + height/2]
        self.whiteColour = [255]*4
        
    def fieldRange(self):
        #circle around point, will need to do this for each point around the actual surface

    def distanceToWall(self, point_x, point_y):
        #right, lets have some fun with vector maths :P
        
        

    def getVertices(self):
        return self.vertexList

    def getColour(self):
        return self.whiteColour

    def getVertexNum(self):
        return self.vertexNumber
