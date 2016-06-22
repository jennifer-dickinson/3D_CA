# Todo: each object should be able to call an instance of this simulator for independent movement simulation
# Todo: minimum turning radius should be calculated based off of speed]
# http://people.clarkson.edu/~pmarzocc/AE429/AE-429-12.pdf

import defaultValues
import vMath
import standardFuncs
import Queue
import time
import random

def move(plane, updater):
    counter = 0  # This is just to keep track of things
    total_distance_traveled =0  # Also just to keep track of things
    waypoint_counter = 0
    timer = 0
    crash = False

    # Make an option for centralized/decentralized collision avoidance & movement

    # Move the plan in a straight line to the direction of the target waypoint
    while plane.cLoc != plane.tLoc:
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
            #if counter % (main.frequency * main.rate_of_updates) == 0:
            #    print 'Adjusting bearing or elevation!'

        # Move the plane in a straight line if bearing is correct
        else:

            # Position is in total distance traveled over one second divided by the frequency of the update
            # Take vector components and add to current longitude and latitude

            speed = plane.speed  # Get speed from plane
            distance_traveled = plane.speed / defaultValues.FREQUENCY
            total_distance_traveled += distance_traveled

            # Calculate new position
            position = vMath.vector(distance_traveled, plane.cBearing, plane.cElevation)
            new_lat = plane.cLoc.latitude + (position.x / standardFuncs.LATITUDE_TO_METERS)
            new_lon = plane.cLoc.longitude + (position.y / standardFuncs.LONGITUDE_TO_METERS)
            new_alt = plane.cLoc.altitude + position.z

            # Update current location, distance, total distance, target bearing,
            newloc = standardFuncs.loc(new_lat,new_lon,new_alt)
            plane.set_cLoc(newloc)
            updater.update(plane)

            # This is acceptable for now. Should change to us current and prvious location from set_cLoc
            plane.tBearing = standardFuncs.find_bearing(new_lat, new_lon, tlat, tlon)
            plane.tElevation = standardFuncs.elevation_angle(new_lat, new_lon, new_alt, tlat, tlon, talt)

            # haversine's horizontal distance
            plane.distance = standardFuncs.horizontal_distance(new_lat, new_lon, tlat, tlon)

            # haversine's horizontal distance w/ vertical distance taken into account
            plane.tdistance = standardFuncs.total_distance(new_lat, new_lon, new_alt, tlat, tlon, talt)

            try:
                if plane.tdistance < 2:
                    waypoint_counter += 1
                    plane.nextwp()
                    print 'UAV #',plane.id, 'Reached waypoint #', waypoint_counter
            except Queue.Empty:
                print 'UAV #', plane.id, 'Reached last waypoint (#', waypoint_counter, ')'
                print plane.cLoc
                break

            if defaultValues.SIMULATE_TIME:
                time.sleep(defaultValues.DELAY)
            timer += defaultValues.DELAY

            if timer % defaultValues.RATE_OF_UPDATES == 0 and defaultValues.IS_TEST:
                print 'UAV #', plane.id, 'currently located at', plane.cLoc

            uav_positions = updater.read()

            for elem in uav_positions:
                distance = standardFuncs.nt_total_distance(plane.cLoc, elem["cLoc"])
                if distance < 12 and elem["ID"] != plane.id and elem["dead"] == False:
                    time.sleep(random.uniform(0, 1.5))
                    print "UAV ID", plane.id, "has crashed with UAV ID", elem["ID"]
                    crash = True
                    break

            if crash: break
    # Todo: make this pretty
    print 'Total distance traved by UAV #', plane.id, ":", total_distance_traveled, "m"
    print 'Total waypoints achieved:', waypoint_counter
    print "Total target waypoints:", plane.numWayPoints
    print 'Total time spent:', timer, 's'
