import planeGenerator
import movementSimulator
from threading import Thread
import commList
import defaultValues

communicator = commList.uavComm()

communicator.start()
if communicator.isAlive: print "Communicator initialized."

plane = planeGenerator.generate_planes(
    defaultValues.NUM_PLANES,
    defaultValues.NUM_WAY_POINTS,
    defaultValues.GRID_SIZE,
    communicator
)

planeMover = list()

for i in range(0, defaultValues.NUM_PLANES):
   planeMover.append(Thread(target=movementSimulator.move, args=(plane[i], communicator, 0)))

for i in range(0, defaultValues.NUM_PLANES):
    planeMover[i].start()

while communicator.isAlive():
    pass

print "Communicator terminated."
