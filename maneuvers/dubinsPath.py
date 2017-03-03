"""
    Copyright (C) 2017  Jennifer Salas

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# This is a straight adaptation from David Jones' RIPNA Algorithm in C++ to Python
from math import fabs, radians, cos, sin

from defaultValues import *
from standardFuncs import *

logger()

TIME_STEP = 1.0  # Is this the same as their delay?
MPS_WAYPOINT_MULTIPLIER = 2


def takeDubinsPath(plane):
    waypoint = plane.tLoc

    minTurnRadius = 0.75 * MIN_TURN_RAD
    wpBearing = plane.tBearing

    cBearingCardinal = to_cardinal(plane.cBearing)
    cBearingCartesian = to_cartesian(plane.cBearing)

    if fabs(cBearingCardinal) < 90:
        if (wpBearing < cBearingCartesian) and (wpBearing > manipulate_angle(cBearingCartesian - 180)):
            destOnRight = True
        else:
            destOnRight = False
    else:
        if (wpBearing > cBearingCartesian) and (wpBearing < manipulate_angle(cBearingCartesian - 180)):
            destOnRight = False
        else:
            destOnRight = True

    circleCenter = calculateLoopingCircleCenter(plane, minTurnRadius, destOnRight)

    if findDistance(circleCenter, plane.tLoc) < minTurnRadius:
        logging.info("UAV #%3i performing a dubins path adjustment." % plane.id)
        logging.info("Circle center for UAV #%3i set to %s" % (plane.id, circleCenter))
        plane.avoid = True
        plane.avoidanceWaypoint = calculateWaypoint(plane, minTurnRadius, not destOnRight)
        return plane.avoidanceWaypoint
    else:
        plane.avoid = False


def calculateLoopingCircleCenter(plane, turnRadius, turnRight):
    # Todo: adapt dubins path to 3 dimensions

    if turnRight:
        angle = radians(plane.cBearing - 90 - 22.5)
    else:
        angle = radians(plane.cBearing + 90 + 22.5)

    # Todo: Adapt this to haversine's formula
    xdiff = turnRadius * cos(angle)
    ydiff = turnRadius * sin(angle)
    zdiff = 0  # just a place holder

    # TODO: Double check if this method will work with existing straightline formula

    lon = plane.cLoc["Longitude"] + xdiff / LONGITUDE_TO_METERS
    lat = plane.cLoc["Latitude"] + ydiff / LATITUDE_TO_METERS
    alt = plane.cLoc["Altitude"] + zdiff

    circleCenter = {"Longitude": lon, "Latitude": lat, "Altitude": alt}
    return circleCenter


def calculateWaypoint(plane, turningRadius, turnRight):
    V = DEFAULT_UAV_SPEED * MPS_WAYPOINT_MULTIPLIER
    delta_T = TIME_STEP
    cartBearing = radians(plane.cBearing)  # Must return in radians
    delta_psi = V / turningRadius * delta_T

    if turnRight: delta_psi *= -1.0  # Reverse direction
    logging.warning("Delta psi: %f", delta_psi)
    psi = (cartBearing + delta_psi)

    V *= MPS_WAYPOINT_MULTIPLIER

    delta_lon = V * cos(psi) / LONGITUDE_TO_METERS
    delta_lat = V * sin(psi) / LATITUDE_TO_METERS
    delta_alt = 0  # Just a place holder

    lon = plane.cLoc["Longitude"] + delta_lon
    lat = plane.cLoc["Latitude"] + delta_lat
    alt = plane.cLoc["Altitude"] + delta_alt

    waypoint = {"Longitude": lon, "Latitude": lat, "Altitude": alt}
    distance = totalDistance(plane.cLoc, waypoint)
    logging.info("UAV #%3i avoidance waypoint at %s." % (plane.id, waypoint))
    logging.info("UAV #%3i %3.1f meters away from avoidance waypoint." % (plane.id, distance))
    return waypoint
