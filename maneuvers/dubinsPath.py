# This is a straight adaptation from David Jones' RIPNA Algorithm in C++ to Python
from standardFuncs import *
from defaultValues import *
from math import fabs, radians, degrees, cos, sin
import logging
logger()



TIME_STEP = 1.0 # Is this the same as their delay?
MPS_WAYPOINT_MULTIPLIER =	2

def takeDubinsPath (plane):
    waypoint = plane.tLoc

    minTurnRadius = 0.75 * MIN_TURN_RAD
    wpBearing = plane.tBearing

    cBearingCardinal = to_cardinal(plane.cBearing)
    cBearingCartesian = to_cartesian(plane.cBearing)

    if  fabs(cBearingCardinal) < 90:
        if (wpBearing < cBearingCartesian) and (wpBearing > manipulate_angle(cBearingCartesian-180)):
            destOnRight = True
        else: destOnRight = False
    else:
        if (wpBearing > cBearingCartesian) and (wpBearing < manipulate_angle(cBearingCartesian - 180)):
            destOnRight = False
        else: destOnRight = True

    circleCenter = calculateLoopingCircleCenter(plane, minTurnRadius, destOnRight)
    circleCenter.altitude = plane.cLoc.altitude

    if findDistance(circleCenter, plane.tLoc) < minTurnRadius:
        logging.info("UAV #%3i performing a dubins path adjustment." % plane.id)
        plane.avoid = True

        plane.avoidanceWaypoint = calculateWaypoint(plane, minTurnRadius, not destOnRight)
        return plane.avoidanceWaypoint
    else:pass

def calculateLoopingCircleCenter(plane,  turnRadius, turnRight):
    circleCenter = loc("","","")

    # Todo: adapt dubins path to 3 dimensions
    circleCenter.altitude = plane.cLoc.altitude

    if turnRight:
        angle = radians(plane.cBearing - 90 - 22.5)
    else:
        angle = radians(plane.cBearing + 90 + 22.5)


    # Todo: Adapt this to haversine's formula
    xdiff = turnRadius * cos(angle)
    ydiff = turnRadius * sin(angle)

    circleCenter.longitude = plane.cLoc.longitude + xdiff/LONGITUDE_TO_METERS
    circleCenter.latitude = plane.cLoc.latitude + ydiff/LATITUDE_TO_METERS

    return circleCenter

def calculateWaypoint(plane, turningRadius, turnRight):
    V = DEFAULT_UAV_SPEED * MPS_WAYPOINT_MULTIPLIER
    delta_T = TIME_STEP
    cartBearing = radians(plane.cBearing) # Must return in radians
    delta_psi = V / turningRadius * delta_T

    if turnRight delta_psi *= -1.0 #Reverse direction
    logging.warning ("Delta psi: %f", delta_psi)
    psi = (cartBearing + delta_psi)

    V *= MPS_WAYPOINT_MULTIPLIER

    delta_lon = V * cos(psi)/DELTA_LON_TO_METERS
    delta_lat = V * sin(psi)/DELTA_LAT_TO_METERS
    delta_alt = 0 # Just a place holder

    lon = plane.cLoc.longitude + delta_lon
    lat = plane.cLoc.latitude + delta_lat
    alt = plane.cLoc.altitude + delta_alt

    waypoint = loc(lon,lat,alt)
    distance = totalDistance(plane.cLoc, waypoint)
    logging.info("UAV #%3i avoidance waypoint at %s." % waypoint)
    logging.info("UAV #%3i %3.1f meters away from avoidance waypoint." % distance)
