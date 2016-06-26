# This is a straight adaptation from Jones' RIPNA Algorithm in C++ to Python
from standardFuncs import *
from defaultValues import *
from math import fabs, radians, degrees, cos, sin
import logging
logger()

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
        logging.info("UAV #%3ierforming a dubins path adjustment." % plane.id)
        return calculateWaypoint(plane, minTurnRadius, not destOnRight)
    else: pass

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

def calculateWaypoint(plane, minTurnRad, destOnRight):