import logging
import time

import defaultValues
import standardFuncs

from maneuvers import straightLine, dubinsPath


def move(plane, globalCommunicator, planeComm):
    stop = False

    while not stop and not plane.dead:

        # If plane distance is less than turning radius, check dubins path. This should be set on or off in settings.

        # Use decentralized communication and collision detectance.
        if not defaultValues.CENTRALIZED:
            uav_positions = plane.map
            for elem in uav_positions:
                distance = standardFuncs.totalDistance(plane.cLoc, elem["Location"])
                if distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["Dead"] == False:
                    plane.dead = True
                    plane.killedBy = elem["ID"]
                    stop = True
                if elem["KilledBy"] == plane.id:
                    plane.dead = True
                    plane.killedBy = elem["ID"]
                    stop = True

        # Default to centralized communication and collision detectance.
        else:
            uav_positions = globalCommunicator.receive(plane)
            for elem in uav_positions:
                distance = standardFuncs.totalDistance(plane.cLoc, elem["cLoc"])
                if distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["dead"] == False:
                    plane.dead = True
                    plane.killedBy = elem["ID"]
                    stop = True
                if elem["ID"] == plane.id and elem["dead"] == True:
                    plane.dead = True
                    plane.killedBy = elem["killedBy"]
                    stop = True

        # Check to see if UAV has reached the waypoint or completed mission.
        if (plane.tdistance < defaultValues.WAYPOINT_DISTANCE) and (plane.wpAchieved <= plane.numWayPoints):
            plane.wpAchieved += 1
            if plane.wpAchieved < plane.numWayPoints:
                plane.nextwp()
            logging.info("UAV #%3i reached waypoint #%i." % (plane.id, plane.wpAchieved))
        if plane.wpAchieved >= plane.numWayPoints:
            stop = True
            logging.info("UAV #%3i reached all waypoints." % plane.id)

        if plane.dead:
            print "UAV #%3i has crashed with UAV #%3i" % (plane.id, plane.killedBy)
        if plane.wpAchieved == plane.numWayPoints: print "UAV #%3i reached all waypoints." % plane.id

        if plane.tdistance <= defaultValues.MIN_TURN_RAD:
            # logging.info("UAV #%3i checking for dubins path." % plane.id)
            dubinsPath.takeDubinsPath(plane)
            pass

        straightLine.straightline(plane)

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