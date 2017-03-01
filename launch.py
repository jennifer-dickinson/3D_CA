import logging
import time

import centralizedComm
import decentralizedComm
import planeGenerator
import standardFuncs

import argumentsplitter

import sys


def main():

    args = argumentsplitter.argParser()

    # Print communicator thread logs
    standardFuncs.logger()

    logging.info('Started')

    print("Simulating UAV flights.... this may take a while.")

    communicator = centralizedComm.uavComm() if args.CENTRALIZED else decentralizedComm.synchronizer(args.NUM_PLANES)

    planeGenerator.PlaneCollection(args, communicator)

    sys.exit(0)


if __name__ == '__main__':
    main()
