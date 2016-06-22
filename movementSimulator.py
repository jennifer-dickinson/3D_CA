# Todo: each object should be able to call an instance of this simulator for independent movement simulation
# Todo: minimum turning radius should be calculated based off of speed]
# http://people.clarkson.edu/~pmarzocc/AE429/AE-429-12.pdf

from standardFuncs import *
from defaultValues import *

import main
import vMath
import standardFuncs
import collections
import Queue

def move(plane):
    counter = 0  # This is just to keep track of things
    total_distance_traveled =0  # Also just to keep track of things
    waypoint_counter = 0
    seconds = 0

    # Move the plan in a straight line to the direction of the target waypoint
    while plane.cLoc != plane.tLoc:
        # find distance to target location

        clat = plane.cLoc.latitude
        clon = plane.cLoc.longitude
        calt = plane.cLoc.altitude

        tlat = plane.tLoc.latitude
        tlon = plane.tLoc.longitude
        talt = plane.tLoc.altitude

        plane.distance = horizontal_distance(clat, clon, tlat, tlon)
        plane.tdistance = total_distance(clat, clon, calt, tlat, tlon, talt)

        # This is a temporary fix for adjusting bearing and elevation
        # Todo: with each adjustment, calculate a distance travled
        if plane.cbearing != plane.tbearing or plane.celevation != plane.televation:

            plane.cbearing = plane.tbearing
            plane.celevation = plane.televation
            #if counter % (main.frequency * main.rate_of_updates) == 0:
            #    print 'Adjusting bearing or elevation!'

        # Move the plane in a straight line if bearing is correct
        else:

            # Position is in total distance traveled over one second divided by the frequency of the update
            # Take vector components and add to current longitude and latitude

            speed = plane.speed  # Get speed from plane
            distance_traveled = plane.speed / FREQUENCY
            total_distance_traveled += distance_traveled

            # Calculate new position
            position = vMath.vector(distance_traveled, plane.cbearing, plane.celevation)
            new_lat = plane.cLoc.latitude + (position.x / standardFuncs.LATITUDE_TO_METERS)
            new_lon = plane.cLoc.longitude + (position.y / standardFuncs.LONGITUDE_TO_METERS)
            new_alt = plane.cLoc.altitude + position.z

            #Update current location, distance, total distance, target bearing,
            newloc = loc(new_lat,new_lon,new_alt)
            plane.set_cLoc(newloc)
            plane.tbearing = find_bearing(new_lat, new_lon, tlat, tlon)
            plane.televation = elevation_angle(new_lat, new_lon, new_alt, tlat, tlon, talt)
            plane.distance = horizontal_distance(new_lat, new_lon, tlat, tlon)
            plane.tdistance = total_distance(new_lat, new_lon, new_alt, tlat, tlon, talt)
            counter += 1

            if counter % (FREQUENCY * RATE_OF_UPDATES) == 0:
                #print 'currently located at', plane.cLoc
                counter = 0
                seconds += 1


            try:
                if plane.tdistance < 2:
                    waypoint_counter += 1
                    plane.nextwp()
                    print 'UAV #',plane.id, 'Reached waypoint #', waypoint_counter
            except Queue.Empty:
                print 'UAV #', plane.id, 'Reached last waypoint (#', waypoint_counter, ')'
                break


    print 'Total distance traved by UAV #', plane.id, "is", total_distance_traveled, "meters"
    print 'Total time spent:', seconds