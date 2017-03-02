import standardFuncs
import vMath

standardFuncs.logger()


def straightline(plane):
    # Simple movement in a straight line with a modified adaptation of dubins path.
    # Working: UAV bearing and elevation update is working. Dubin's avoidance is working.

    msg = ["WP %2i" % plane.wpAchieved, "MTA: %.2f" % (plane.maxTurnAngle * plane.args.DELAY)]
    MAX_TURN_ANGLE = plane.maxTurnAngle

    if plane.avoid:
        if plane.tdistance >= 2 * MAX_TURN_ANGLE:
            plane.avoid = False
    else:
        target = plane.tLoc

    deltaBearing = standardFuncs.relativeAngle(plane.cBearing, plane.tBearing)

    msg.append("Current Bearing: %7.2f" % plane.cBearing)
    msg.append("Target Bearing:  %7.2f" % plane.tBearing)
    msg.append("Relative Angle to Target: %7.2f" % deltaBearing)

    # if the UAV is
    if not (((plane.tdistance <= plane.minTurningRadius + plane.args.WAYPOINT_DISTANCE and abs(
            deltaBearing) >= MAX_TURN_ANGLE)) or plane.avoid):

        if abs(deltaBearing) <= MAX_TURN_ANGLE * plane.args.DELAY:
            # cBearing = tBearing;
            plane.cBearing = plane.tBearing
            msg.append("Turn ok")

        elif 0 < deltaBearing < 180:
            # print("current bearing - max turning angle = ", cBearing - MAX_TURN_ANGLE)
            msg.append("Turning right")
            plane.cBearing = plane.cBearing - (MAX_TURN_ANGLE * plane.args.DELAY)


        else:
            # print("current bearing + max turning angle = ", cBearing + MAX_TURN_ANGLE)
            msg.append("Turning left")
            plane.cBearing = plane.cBearing + (MAX_TURN_ANGLE * plane.args.DELAY)

        msg.append("New Bearing: %.2f" % plane.cBearing)

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

    # print("Total Distance: ", standardFuncs.totalDistance(newLoc, plane.cLoc))


    msg.append("Current bearing: %.2f" % plane.cBearing)
    msg.append("Target bearing: %.2f" % plane.tBearing)
    msg.append("Target distance: %.2f" % plane.tdistance)
    plane.updateTelemetry(newLoc)
    # print(msg)
