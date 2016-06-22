from planeGenerator import generate_planes
from movementSimulator import move
from threading import Thread
from defaultValues import *


plane = generate_planes(NUM_PLANES, NUM_WAY_POINTS, GRID_SIZE)

planeMover = list()

for i in range(0, NUM_PLANES):
    planeMover.append(Thread(target=move, args=(plane[i],)))

for i in range(0, NUM_PLANES):
    planeMover[i].start()

for i in range(0, NUM_PLANES):
    planeMover[i].join()