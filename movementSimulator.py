# Todo: each object should be able to call an instance of this simulator for independent movement simulation
# Todo: minimum turning radius should be calculated based off of speed]
# http://people.clarkson.edu/~pmarzocc/AE429/AE-429-12.pdf

import defaultValues
import vMath
import standardFuncs
import Queue
import time
import random

def move(plane, communicator):
    counter = 0  # This is just to keep track of things
    total_distance_traveled =0  # Also just to keep track of things
    waypoint_counter = 0
    timer = 0

    # Todo: Make an option for centralized/decentralized collision avoidance & movement

    # Move the plan in a straight line to the direction of the target waypoint
    while plane.dead == False:

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

        plane.distance = standardFuncs.horizontal_distance(clat, clon, tlat, tlon)
        plane.tdistance = standardFuncs.total_distance(clat, clon, calt, tlat, tlon, talt)

        # This is a temporary fix for adjusting bearing and elevation
        # Todo: with each adjustment, calculate a distance travled
        if plane.cBearing != plane.tBearing or plane.cElevation != plane.tElevation:

            plane.cBearing = plane.tBearing
            plane.cElevation = plane.tElevation

        # Move the plane in a straight line if bearing is correct
        else:

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

            # Update current location, distance, total distance, target bearing,
            newloc = standardFuncs.loc(new_lat,new_lon,new_alt)
            plane.set_cLoc(newloc)

            # This is acceptable for now. Should change to us current and prvious location from set_cLoc
            plane.tBearing = standardFuncs.find_bearing(new_lat, new_lon, tlat, tlon)
            plane.tElevation = standardFuncs.elevation_angle(new_lat, new_lon, new_alt, tlat, tlon, talt)

            # haversine's horizontal distance
            plane.distance = standardFuncs.horizontal_distance(new_lat, new_lon, tlat, tlon)

            # haversine's horizontal distance w/ vertical distance taken into account
            plane.tdistance = standardFuncs.total_distance(new_lat, new_lon, new_alt, tlat, tlon, talt)

        if timer % defaultValues.RATE_OF_UPDATES == 0 and defaultValues.IS_TEST:
            print 'UAV #', plane.id, 'currently located at', plane.cLoc

        uav_positions = communicator.read()

        for elem in uav_positions:
            distance = standardFuncs.nt_total_distance(plane.cLoc, elem["cLoc"])
            if (distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["dead"] == False):
                # time.sleep(random.uniform(0, .001))  # Just so that the console doesn't get screwed up
                plane.dead = True
                plane.killedBy = elem["ID"]
                break
            elif elem["ID"] == plane.id and elem["dead"] == True:
                plane.dead = True
                plane.killedBy = elem["killedBy"]
                break


        if plane.tdistance < defaultValues.DISTANCE_FOR_SUCCESS:
            plane.wpAchieved += 1
            try: plane.nextwp()
            except Queue.Empty:
                communicator.update(plane)
                #print 'UAV #%.0f reached last waypoint.' % plane.id
                break

        communicator.update(plane)

    # Todo: make this pretty
    time.sleep(random.uniform(0, 0.1))
    if plane.dead: print ("UAV #%.0f has crashed!!!!!!!!!!!!!!!!!!!!!" % plane.id)
