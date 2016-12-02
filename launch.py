import logging
import time

import centralizedComm
import decentralizedComm
import planeGenerator
import standardFuncs

import argumentsplitter


def main():

    args = argumentsplitter.argParser()

    # Start printing information to a log file. This overwrites all previous data!
    standardFuncs.logger()

    logging.info('Started')

    print("Simulating UAV flights.... this may take a while.")

    if not args.CENTRALIZED:
        communicator = decentralizedComm.synchronizer(args.NUM_PLANES)

    else:
        communicator = centralizedComm.uavComm()

    uavList = planeGenerator.generate_planes(args, communicator)

    while communicator.isAlive():
        pass
    logging.info("Global communicator terminated: %s" % communicator)
    time.sleep(.01)
    print("Simulation complete.")

    uav_status(uavList)


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
