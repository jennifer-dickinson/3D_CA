import planeGenerator
import movementSimulator
from threading import Thread
import commList
import defaultValues
import communicator
import time

qu = commList.uavComm()
plane = planeGenerator.generate_planes(defaultValues.NUM_PLANES, defaultValues.NUM_WAY_POINTS, defaultValues.GRID_SIZE, qu)

planeMover = list()
qu.start()
for i in range(0, defaultValues.NUM_PLANES):
   planeMover.append(Thread(target=movementSimulator.move, args=(plane[i], qu)))
   print 'plane generated'

for i in range(0, defaultValues.NUM_PLANES):
    planeMover[i].start()

for i in range(0, defaultValues.NUM_PLANES):
    planeMover[i].join()

qu.stop()