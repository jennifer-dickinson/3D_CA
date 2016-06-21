# Will modify vMath.cpp under ROS to be included here... eventually

import math
from standardFuncs import *

class vector:
    def __init__(self, magnitude, direction, elevation):
        self.magnitude = magnitude
        self.direction = direction

        #
        if 0 <= elevation <= 90 :
            self.elevation = 90 - math.fabs(elevation)
        elif -90 <= elevation < 0 :
            self.elevation = 90 + math.fabs(elevation)
        else:
            print 'You made an error'

        self.x = magnitude * math.sin(math.radians(self.elevation)) * math.cos(math.radians(direction))
        self.y = magnitude * math.sin(math.radians(self.elevation)) * math.sin(math.radians(direction))
        self.z = magnitude * math.cos(math.radians(self.elevation))

