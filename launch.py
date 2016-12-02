import logging
import time

import centralizedComm
import decentralizedComm
import defaultValues
import planeGenerator
import standardFuncs
import sys

import argumentsplitter


def main():

    args = argumentsplitter.argParser()
    argumentsplitter.displayArgs(args)

    print("Number of arguments: ", len(sys.argv))
    print("Argument list: ", str(sys.argv))

    # Start printing information to a log file. This overwrites all previous data!
    standardFuncs.logger()

    logging.info('Started')

    print("Simulating UAV flights.... this may take a while.")
    if not defaultValues.CENTRALIZED:
        print("Running simulation in decentralized mode.")
    else:
        print("Running simulation in centralized mode.")

    if not defaultValues.COLLISION_DETECTANCE:
        print("No collision detection set.")
    else:
        print("Collision detection set.")
    if not defaultValues.CENTRALIZED:
        communicator = decentralizedComm.synchronizer(defaultValues.NUM_PLANES)

    else:
        communicator = centralizedComm.uavComm()

    list = planeGenerator.generate_planes(
        defaultValues.NUM_PLANES,
        defaultValues.NUM_WAY_POINTS,
        defaultValues.GRID_SIZE,
        communicator
    )

    while communicator.isAlive():
        pass
    logging.info("Global communicator terminated: %s" % communicator)
    time.sleep(.01)
    print("Simulation complete.")

    uav_status(list)


def uav_status(plane):
    # Print status for each UAV.
    title = '\n%-3s  %-40s  %-6s  %-4s  %-5s  %-10s ' % (
        'ID#',
        'Final Location',
        'Dist.',
        'WPTS',
        'Dead?',
        'Killed By?'
    )
    print(title)
    line = ""
    for i in title:
        line += "_"
    print(line)

    for i in range(len(plane)):
        if plane[i].dead:
            killed = "UAV #%s" % plane[i].killedBy
        else:
            killed = "N/A"
        location = "(%.7f%s, %.7f%s, %.1f m)" % (
            plane[i].cLoc["Latitude"], standardFuncs.DEGREE,
            plane[i].cLoc["Longitude"], standardFuncs.DEGREE,
            plane[i].cLoc["Altitude"],
        )
        print('%3i  %-40s  %6.1f  %4s  %-5s  %-10s' % (
            plane[i].id,
            location,
            plane[i].distanceTraveled,
            plane[i].wpAchieved,
            plane[i].dead,
            killed
        ))


if __name__ == '__main__':
    main()
