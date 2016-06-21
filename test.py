import Queue
from planeGenerator import generate_planes
import movementSimulator
import vMath
import standardFuncs
import math


numPlanes = 12
numWayPoints = 20
gridSize = 1000

plane = generate_planes(numPlanes, numWayPoints, gridSize)
movementSimulator.move(plane[11]) #This just makes the plane move. Will eventually add threading to this later.