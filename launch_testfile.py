import planeGenerator
import movementSimulator
from threading import Thread
import centralizedComm
import decentralizedComm
import defaultValues
import logging
from standardFuncs import logger

defaultValues.CENTRALIZED = False
defaultValues.NUM_PLANES = 2
defaultValues.GRID_SIZE = 20
defaultValues.NUM_WAY_POINTS = 10


def main():
    logger()

    logging.info('Started')

    if not defaultValues.CENTRALIZED:
        communicator = decentralizedComm.synchronizer(defaultValues.NUM_PLANES)

    else:
        communicator = centralizedComm.uavComm()

    print ("Simulating UAV flights.... this may take a while.")

    # Wait for communicator to start before next step.
    while not communicator.is_alive():
        pass

    planeGenerator.generate_planes(
        defaultValues.NUM_PLANES,
        defaultValues.NUM_WAY_POINTS,
        defaultValues.GRID_SIZE,
        communicator
    )

    while communicator.isAlive():
        pass
    logging.info("Global communicator terminated: %s" % communicator)
    print ("Simulation complete.")


if __name__ == '__main__':
    main()
