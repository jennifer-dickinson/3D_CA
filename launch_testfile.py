import planeGenerator
import movementSimulator
from threading import Thread
import centralizedComm
import decentralizedComm
import defaultValues
import logging
from standardFuncs import logger

defaultValues.CENTRALIZED = True
defaultValues.NUM_PLANES = 20
defaultValues.GRID_SIZE = 20
defaultValues.NUM_WAY_POINTS = 10

def main():
    logger()

    logging.info('Started')

    if not defaultValues.CENTRALIZED:
        communicator = decentralizedComm.synchronizer()
    else:
        communicator = centralizedComm.uavComm()

    communicator.start()

    planeGenerator.generate_planes(
        defaultValues.NUM_PLANES,
        defaultValues.NUM_WAY_POINTS,
        defaultValues.GRID_SIZE,
        communicator
    )

    while communicator.isAlive():
        pass
    logging.info('Finished running simulation.')


if __name__ == '__main__':
    main()
