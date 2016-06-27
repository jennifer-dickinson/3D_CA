# Todo: each object should be able to call an instance of this simulator for independent movement simulation
# Todo: minimum turning radius should be calculated based off of speed]
# http://people.clarkson.edu/~pmarzocc/AE429/AE-429-12.pdf

import defaultValues
import vMath
import standardFuncs
import Queue
import time
import random

def move(plane, communicator, method):
    timer = 0
    stop = False

    # Todo: Make an option for centralized/decentralized collision avoidance & movement
    # Move the plan in a straight line to the direction of the target waypoint
    while not stop and not plane.dead:

        # Simulate time by delaying planes update. Will need this for GUI.
        if defaultValues.SIMULATE_TIME:
            time.sleep(defaultValues.DELAY)
        timer += defaultValues.DELAY

        # find distance to target location

        clat = plane.cLoc.latitude
        clon = plane.cLoc.longitude
        calt = plane.cLoc.altitude

        tlat = plane.tLoc.latitude
        tlon = plane.tLoc.longitude
        talt = plane.tLoc.altitude

        plane.distance = standardFuncs.findDistance(plane.cLoc, plane.tLoc)
        plane.tdistance = standardFuncs.totalDistance(plane.cLoc, plane.tLoc)

        # This is a temporary fix for adjusting bearing and elevation
        # Todo: with each adjustment, calculate a distance travled
        #if plane.cBearing != plane.tBearing or plane.cElevation != plane.tElevation:

        #    plane.cBearing = plane.tBearing
        #    plane.cElevation = plane.tElevation

        # Move the plane in a straight line if bearing is correct
        if True: # Was supposed to be elif, until plane bearing adjustment is made leave as if True.

            plane.cBearing = plane.tBearing
            plane.cElevation = plane.tElevation

            # Position is in total distance traveled over one second multiplied by time (DELAY)
            # Take vector components and add to current longitude and latitude

            speed = plane.speed  # Get speed from plane
            distanceTraveled = plane.speed * defaultValues.DELAY
            plane.distanceTraveled += distanceTraveled

            # Calculate new position
            position = vMath.vector(distanceTraveled, plane.cBearing, plane.cElevation)

            new_lat = plane.cLoc.latitude + (position.x / standardFuncs.LATITUDE_TO_METERS)
            new_lon = plane.cLoc.longitude + (position.y / standardFuncs.LONGITUDE_TO_METERS)
            new_alt = plane.cLoc.altitude + position.z

            newLoc = standardFuncs.loc(new_lat,new_lon,new_alt)

            # Update current location, distance, total distance, target bearing,
            newloc = standardFuncs.loc(new_lat,new_lon,new_alt)
            plane.set_cLoc(newloc)

            # This is acceptable for now. Should change to us current and prvious location from set_cLoc
            plane.tBearing = standardFuncs.find_bearing(newLoc, plane.tLoc)
            plane.tElevation = standardFuncs.elevation_angle(newLoc,plane.tLoc)

            # haversine's horizontal distance
            plane.distance = standardFuncs.findDistance(newLoc, plane.tLoc)

            # haversine's horizontal distance w/ vertical distance taken into account
            plane.tdistance = standardFuncs.totalDistance(newLoc, plane.tLoc)

        if timer % defaultValues.RATE_OF_UPDATES == 0 and defaultValues.IS_TEST:
            print 'UAV #', plane.id, 'currently located at', plane.cLoc

        uav_positions = communicator.read(plane)

        for elem in uav_positions:
            distance = standardFuncs.totalDistance(plane.cLoc, elem["cLoc"])
            if (distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["dead"] == False):
                # time.sleep(random.uniform(0, .001))  # Just so that the console doesn't get screwed up
                plane.dead = True
                plane.killedBy = elem["ID"]
                stop = True
            elif elem["ID"] == plane.id and elem["dead"] == True:
                plane.dead = True
                plane.killedBy = elem["killedBy"]
                stop = True

        # Move through queue to next waypoint, or if done stop thread.
        if (plane.tdistance < defaultValues.WAYPOINT_DISTANCE) and (plane.wpAchieved <= plane.numWayPoints):
            plane.wpAchieved += 1
            if plane.wpAchieved < plane.numWayPoints:
                plane.nextwp()
        if plane.wpAchieved >= plane.numWayPoints: stop = True

        communicator.update(plane)

    # Todo: make this pretty
    if plane.dead: print "\r%-80s" % "UAV #%3i has crashed!!" % plane.id
    if plane.wpAchieved == plane.numWayPoints: print "\r%-80s" % "UAV #%3i reached all waypoints." % plane.id
