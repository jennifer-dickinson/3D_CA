import logging

import defaultValues
import standardFuncs

from maneuvers import straightLine, dubinsPath


def move(plane, globalCommunicator, planeComm):
    stop = False

    while not stop and not plane.dead:

        if defaultValues.COLLISION_DETECTANCE:
            # Use decentralized communication and collision detection or default to centralized.
            if not defaultValues.CENTRALIZED:
                uav_positions = plane.map
            else:
                uav_positions = globalCommunicator.receive(plane)

            for elem in uav_positions:
                distance = standardFuncs.totalDistance(plane.cLoc, elem["Location"])
                if distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["Dead"] == False:
                    plane.dead = True
                    plane.killedBy = elem["ID"]
                    stop = True
                    break
                if elem["killedBy"] == plane.id:  # and elem["dead"] == True:
                    plane.dead = True
                    plane.killedBy = elem["ID"]
                    stop = True
                    break

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
            print("UAV #%3i has crashed with UAV #%3i" % (plane.id, plane.killedBy))
        if plane.wpAchieved == plane.numWayPoints: print("UAV #%3i reached all waypoints." % plane.id)

        # if plane.tdistance <= (3 * defaultValues.MIN_TURN_RAD):
        #     # logging.info("UAV #%3i checking for dubins path." % plane.id)
        #     dubinsPath.takeDubinsPath(plane)
        #     pass

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
