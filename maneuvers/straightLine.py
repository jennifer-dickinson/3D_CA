import logging

import standardFuncs
import defaultValues
import vMath

standardFuncs.logger()


# TODO: Adapt this to waypoints
def straightline(plane):
    if plane.avoid:

        target = plane.avoidanceWaypoint
        logging.info("UAV #3i is performing an avoidance maneuver." % plane.id)
        wpBearing = standardFuncs.find_bearing(plane.cLoc, target)

    else:
        target = plane.tLoc
        wpBearing = plane.tBearing

    plane.cBearing = plane.tBearing
    plane.cElevation = plane.tElevation

    # Find the difference in target and current angles of elevation and bearing.
    #  delta_theta = plane.cBearing - to_cardi(standardFuncs.find_bearing(plane.cLoc, target))
    # if abs(delta_theta) > defaultValues.MAX_TURN_ANGLE:
    #     delta_theta = standardFuncs.find_sign(delta_theta) * defaultValues.MAX_turn_ANGLE
    #
    # if 0 < delta_theta < 180:
    #     # The target is on the right side
    #     newbearing = plane.cBearing + abs(delta_theta)
    # if -180 < delta_theta < 0:
    #     newbearing = plane.cBearing - delta_theta
    # if delta_theta == 0: pass


    # cBearingCardinal = standardFuncs.to_cardinal(plane.cBearing)
    # cBearingCartesian = standardFuncs.to_cartesian(plane.cBearing)
    #
    # if math.fabs(cBearingCardinal) < 90:
    #     if (wpBearing < cBearingCartesian) and (wpBearing > standardFuncs.manpulate_angle(cBearingCartesian - 180)):
    #         destOnRight = True
    #     else:
    #         destOnRight = False
    # else:
    #     if (wpBearing > cBearingCartesian) and (wpBearing < standardFuncs.manipulate_angle(cBearingCartesian - 180)):
    #         destOnRight = False
    #     else:
    #         destOnRight = True



    # delta_theta = plane.cBearing - wpBearing
    # if destOnRight:


    # If difference is greater than maximum turning radius and maximum inclination angle,
    # add maximum inclination angle to current inclination
    # add maximum bearing to current bearing.


    speed = plane.speed  # Get speed from plane
    distanceTraveled = plane.speed * defaultValues.DELAY  # Get frequency of updates.
    plane.distanceTraveled += distanceTraveled  # The total distance travelled.

    # Calculate new position
    position = vMath.vector(distanceTraveled, plane.cBearing, plane.cElevation)

    new_lat = plane.cLoc.latitude + (position.x / standardFuncs.LATITUDE_TO_METERS)
    new_lon = plane.cLoc.longitude + (position.y / standardFuncs.LONGITUDE_TO_METERS)
    new_alt = plane.cLoc.altitude + position.z

    newLoc = standardFuncs.loc(new_lat, new_lon, new_alt)

    # Update current location, distance, total distance, target bearing,
    newloc = standardFuncs.loc(new_lat, new_lon, new_alt)
    plane.set_cLoc(newloc)

    # Calculate new bearing
    plane.cBearing = standardFuncs.find_bearing(plane.pLoc, plane.cLoc)
    plane.cElevation = standardFuncs.elevation_angle(plane.pLoc, plane.cLoc)

    # Calculate new elevation
    plane.tBearing = standardFuncs.find_bearing(newLoc, plane.tLoc)
    plane.tElevation = standardFuncs.elevation_angle(newLoc, plane.tLoc)

    # haversine's horizontal distance
    plane.distance = standardFuncs.findDistance(newLoc, plane.tLoc)

    # haversine's horizontal distance w/ vertical distance taken into account
    plane.tdistance = standardFuncs.totalDistance(newLoc, plane.tLoc)
