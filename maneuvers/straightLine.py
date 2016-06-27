import standardFuncs
import defaultValues
import vMath
import logging
logger()

def straightline (plane)
    plane.cBearing = plane.tBearing
    plane.cElevation = plane.tElevation

    # Position is in total distance traveled over one second multiplied by time (DELAY)
    # Take vector components and add to current longitude and latitude

    speed = plane.speed  # Get speed from plane
    distanceTraveled = plane.speed * defaultValues.DELAY #Get frequency of updates.
    plane.distanceTraveled += distanceTraveled  #The total distance travelled.

    # Calculate new position
    position = vMath.vector(distanceTraveled, plane.cBearing, plane.cElevation)

    new_lat = plane.cLoc.latitude + (position.x / standardFuncs.LATITUDE_TO_METERS)
    new_lon = plane.cLoc.longitude + (position.y / standardFuncs.LONGITUDE_TO_METERS)
    new_alt = plane.cLoc.altitude + position.z

    newLoc = standardFuncs.loc(new_lat,new_lon,new_alt)

    # Update current location, distance, total distance, target bearing,
    newloc = standardFuncs.loc(new_lat,new_lon,new_alt)
    plane.set_cLoc(newloc)

    # Calculate new bearing
    plane.cBearing = standardFuncs.find_bearing(plane.pLoc, plane.cLoc)
    plane.cElevation = standardFuncs.elevation_angle(plane.pLoc, plane.cLoc)

    # Calculate new elevation
    plane.tBearing = standardFuncs.find_bearing(newLoc, plane.tLoc)
    plane.tElevation = standardFuncs.elevation_angle(newLoc,plane.tLoc)

    # haversine's horizontal distance
    plane.distance = standardFuncs.findDistance(newLoc, plane.tLoc)

    # haversine's horizontal distance w/ vertical distance taken into account
    plane.tdistance = standardFuncs.totalDistance(newLoc, plane.tLoc)
