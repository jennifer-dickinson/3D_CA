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
import standardFuncs
import vMath

standardFuncs.logger()


def straightline(plane):
    # Simple movement in a straight line with a modified adaptation of dubins path.
    # Working: UAV bearing and elevation update is working. Dubin's avoidance is working.

    MAX_TURN_ANGLE = plane.maxTurnAngle

    if plane.avoid:
        if plane.tdistance >= 2 * MAX_TURN_ANGLE:
            plane.avoid = False
    else:
        target = plane.tLoc

    deltaBearing = standardFuncs.relativeAngle(plane.cBearing, plane.tBearing)

    # if the UAV is
    if not (((plane.tdistance <= plane.minTurningRadius + plane.args.WAYPOINT_DISTANCE and abs(
            deltaBearing) >= MAX_TURN_ANGLE)) or plane.avoid):

        if abs(deltaBearing) <= MAX_TURN_ANGLE * plane.args.DELAY:
            # cBearing = tBearing;
            plane.cBearing = plane.tBearing

        elif 0 < deltaBearing < 180:
            # print("current bearing - max turning angle = ", cBearing - MAX_TURN_ANGLE)
            plane.cBearing = plane.cBearing - (MAX_TURN_ANGLE * plane.args.DELAY)


        else:
            # print("current bearing + max turning angle = ", cBearing + MAX_TURN_ANGLE)
            plane.cBearing = plane.cBearing + (MAX_TURN_ANGLE * plane.args.DELAY)

    else:
        # print("UAV is within it's minimum turning radius and over it's maximum turning angle")
        plane.avoid = True

    if plane.tElevation > plane.maxElevationAngle:
        plane.cElevation = plane.maxElevationAngle
    elif plane.tElevation < -plane.maxElevationAngle:
        plane.cElevation = -plane.maxElevationAngle
    else:
        plane.cElevation = plane.tElevation

    # Calculate new position
    position = vMath.vector(plane.speed * plane.args.DELAY, plane.cBearing, plane.cElevation)

    new_lat = plane.cLoc["Latitude"] + (position.x / standardFuncs.LATITUDE_TO_METERS)
    new_lon = plane.cLoc["Longitude"] + (position.y / standardFuncs.LONGITUDE_TO_METERS)
    new_alt = plane.cLoc["Altitude"] + position.z

    newLoc = {"Latitude": new_lat, "Longitude": new_lon, "Altitude": new_alt}
    plane.updateTelemetry(newLoc)
