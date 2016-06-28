import planeGenerator
import movementSimulator
from threading import Thread
import centralizedComm
import decentralizedComm
import defaultValues
import logging
from standardFuncs import logger


def main():
    logger()

    logging.info('Started')

    if not defaultValues.CENTRALIZED:
        communicator = decentralizedComm.synchronizer()
    else:
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
        planeMover.append(
            Thread(target=movementSimulator.move, args=(plane[i], communicator)))

    for i in range(0, defaultValues.NUM_PLANES):
        planeMover[i].setDaemon(True)
        planeMover[i].start()

    while communicator.isAlive():
        pass

    logging.info('Communicator terminated.')
    logging.info('Finished')


if __name__ == '__main__':
    main()
