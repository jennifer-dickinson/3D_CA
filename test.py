from planeGenerator import generate_planes
from movementSimulator import move
from threading import Thread

numPlanes = 4
numWayPoints = 10
gridSize = 1000


plane = generate_planes(numPlanes, numWayPoints, gridSize)

planeMover = list()

for i in range(0, numPlanes):
    planeMover.append(Thread(target=move, args=(plane[i],)))

for i in range(0, numPlanes):
    planeMover[i].start()

for i in range(0, numPlanes):
    planeMover[i].join()