# Will modify vMath.cpp under ROS to be included here... eventually

import math


class vector:
    def __init__(self, magnitude, direction, elevation):
        assert magnitude > 0
        assert -180 <= direction < 180
        assert -90 <= elevation <= 90

        self.__magnitude = magnitude
        self.__direction = direction
        self.__elevation = elevation

        self.__x = magnitude * math.sin(math.radians(self.elevation)) * math.cos(math.radians(direction))
        self.__y = magnitude * math.sin(math.radians(self.elevation)) * math.sin(math.radians(direction))
        self.__z = magnitude * math.cos(math.radians(self.elevation))

    def distance(self, x, y, z):
        return math.sqrt(x ** 2 + y ** 2 + z ** 2)

    @property
    def magnitude(self):
        return self.__magnitude

    @property
    def direction(self):
        return self.__direction

    @property
    def elevation(self):
        return self.__elevation

    @property
    def y(self):
        return self.__y

    @property
    def x(self):
        return self.__x

    @property
    def z(self):
        return self.__z

    def __mul__(self, v):
        if isinstance(v, vector):
            # vector multiplication
            x = self.__y * v.z
            y = self.__z * v.x
            z = self.__x * v.y

            direction = math.tan(y / x)
            elevation = math.tan(z / direction)
            magnitude = self.distance(x, y, z)

        else:
            direction = self.__direction
            elevation = self.__elevation
            magnitude = self.__magnitude * v

        return vector(magnitude, direction, elevation)
