# Todo: each object should be able to call an instance of this simulator for independent movement simulation
# Todo: minimum turning radius should be calculated based off of speed]
# http://people.clarkson.edu/~pmarzocc/AE429/AE-429-12.pdf

import defaultValues
import standardFuncs
import time
import logging

from maneuvers import straightLine, dubinsPath


def move(plane, globalCommunicator, planeComm):
    stop = False

    while not stop and not plane.dead:

        # If plane distance is less than turning radius, check dubins path. This should be set on or off in settings.
        if plane.tdistance <= defaultValues.MIN_TURN_RAD:
            # logging.info("UAV #%3i checking for dubins path." % plane.id)
            dubinsPath.takeDubinsPath(plane)
            pass

        # plane.cBearing = plane.tBearing
        plane.cElevation = plane.tElevation

        straightLine.straightline(plane)

        # If decentralized, use map from plane
        if not defaultValues.CENTRALIZED:
            uav_positions = plane.map
        # Default to centralized communication.
        else:
            uav_positions = globalCommunicator.receive(plane)

        for elem in uav_positions:
            distance = standardFuncs.totalDistance(plane.cLoc, elem["cLoc"])
            if (distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["dead"] == False):
                plane.dead = True
                plane.killedBy = elem["ID"]
                stop = True
            elif elem["ID"] == plane.id and elem["dead"] == True:
                plane.dead = True
                plane.killedBy = elem["killedBy"]
                stop = True

        if (plane.tdistance < defaultValues.WAYPOINT_DISTANCE) and (plane.wpAchieved <= plane.numWayPoints):
            plane.wpAchieved += 1
            if plane.wpAchieved < plane.numWayPoints:
                plane.nextwp()
            logging.info("UAV #%3i reached waypoint #%i." % (plane.id, plane.wpAchieved))
        if plane.wpAchieved >= plane.numWayPoints:
            stop = True
            logging.info("UAV #%3i reached all waypoints." % plane.id)

        # Todo: make this pretty
        if plane.dead: print "\r%-80s" % "UAV #%3i has crashed!!" % plane.id
        if plane.wpAchieved == plane.numWayPoints: print "\r%-80s" % "UAV #%3i reached all waypoints." % plane.id

        # Broadcast telemetry through decentralized communication
        if not defaultValues.CENTRALIZED:
            try:
                planeComm.update()
            except:
                logging.fatal("UAV #%3i cannot update to communicator thread: %s" % (plane.id, planeComm))
                plane.dead = True

        # Update telemetry to centralized communication
        else:
            globalCommunicator.update(plane)
