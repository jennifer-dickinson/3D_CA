"""
    Copyright (C) 2018  Jennifer Salas

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


# Will modify vMath.cpp under ROS to be included here... eventually


# Will modify vMath.cpp under ROS to be included here... eventually

import math


class vector:
    def __init__(self, magnitude, direction, elevation):
        self.magnitude = magnitude
        self.direction = direction

        #
        if 0 <= elevation <= 90:
            self.elevation = 90 - math.fabs(elevation)
        elif -90 <= elevation < 0:
            self.elevation = 90 + math.fabs(elevation)
        else:
            print('Why is your UAV upside down?')

        self.x = magnitude * math.sin(math.radians(self.elevation)) * math.cos(math.radians(direction))
        self.y = magnitude * math.sin(math.radians(self.elevation)) * math.sin(math.radians(direction))
        self.z = magnitude * math.cos(math.radians(self.elevation))

# class vector:
#     def __init__(self, magnitude, direction, elevation):
#         assert magnitude > 0
#         assert -180 <= direction < 180
#         assert -90 <= elevation <= 90
#
#         self.__magnitude = magnitude
#         self.__direction = direction
#         self.__elevation = elevation
#
#         self.__x = magnitude * math.sin(math.radians(self.elevation)) * math.cos(math.radians(direction))
#         self.__y = magnitude * math.sin(math.radians(self.elevation)) * math.sin(math.radians(direction))
#         self.__z = magnitude * math.cos(math.radians(self.elevation))
#
#     def distance(self, x, y, z):
#         return math.sqrt(x ** 2 + y ** 2 + z ** 2)
#
#     @property
#     def magnitude(self):
#         return self.__magnitude
#
#     @property
#     def direction(self):
#         return self.__direction
#
#     @property
#     def elevation(self):
#         return self.__elevation
#
#     @property
#     def y(self):
#         return self.__y
#
#     @property
#     def x(self):
#         return self.__x
#
#     @property
#     def z(self):
#         return self.__z
#
#     def __mul__(self, v):
#         if isinstance(v, vector):
#             # vector multiplication
#             x = self.__y * v.z
#             y = self.__z * v.x
#             z = self.__x * v.y
#
#             direction = math.tan(y / x)
#             elevation = math.tan(z / direction)
#             magnitude = self.distance(x, y, z)
#
#         else:
#             direction = self.__direction
#             elevation = self.__elevation
#             magnitude = self.__magnitude * v
#
#         return vector(magnitude, direction, elevation)
