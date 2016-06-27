import planeGenerator
import movementSimulator
from threading import Thread
import centralizedComm
import defaultValues
import logging
from standardFuncs import logger


def main():
    logger()

    logging.info('Started')

    communicator = centralizedComm.uavComm()

    communicator.start()
    logging.info('Communicator initialized.')

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
        planeMover[i].setDaemon(True)
        planeMover[i].start()

    # Just randomly testing certain funcs.


    while communicator.isAlive():
        pass

    logging.info('Communicator terminated.')
    logging.info('Finished')


if __name__ == '__main__':
    main()
