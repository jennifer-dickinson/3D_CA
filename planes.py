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
# This file contains all the information for planes. As of now, it only generates random planes.
import queue

import defaultValues
import standardFuncs


# Plane object will eventually have more parameters
class Plane:
    startPositions = []

    def __init__(self, planid, args):

        self.args = args
        self.id = planid

        self.speed = args.UAV_SPEED  # UAV airspeed in meters per second, 12 meters per second by default
        self.maxElevationAngle = args.MAX_ELEV_ANGLE  # Maximum climbing angle in degrees
        self.maxTurnAngle = args.MAX_TURN_ANGLE
        self.minTurningRadius = args.MIN_TURN_RAD  # Minimum turning radius in meters, should be variable depending on speed
        self.maxBankAngle = None

        self.numWayPoints = args.NUM_WAYPOINTS  # Total number of waypoints assigned to plane
        self.waypoints = queue.Queue()  # Waypoint queue
        self.wpAchieved = 0  # Of waypoints achieved

        self.distance = 0  # Horizontal distance to waypoint in meters
        self.tdistance = 0  # Total distance to waypoint in meters

        self.distanceTraveled = 0  # Total distance traveled in meters

        self.pLoc = None  # Previous location
        self.cLoc = None  # Current location
        self.tLoc = None  # Target location. Will be swapped in queue

        # self.cBearing = None  # Current bearing (Cartesian)
        self.__cBearing = 0
        self.tBearing = None  # Target bearing  (Cartesian)
        self.cElevation = None  # Current elevation (Cartesian)
        self.tElevation = None  # Target elevation  (Cartesian)

        self.avoid = False  # Is the plane performing an avoidance maneuver?
        self.avoidanceWaypoint = None  # Avoidance waypoint (should only be one)

        self.dead = False  # Plane generates UAV and well
        self.killedBy = None  # Records which UAV it crashed with

        self.msg = []  # Any telemetry message received
        self.msgcounter = 0
        self.map = []  # A map of all UAVs
        self.comm = None
        self.path = []

        self.setWaypoints()
        self.setStart()

    @property
    def cBearing(self):
        return self.__cBearing

    @cBearing.setter
    def cBearing(self, value):

        self.__cBearing = value
        if self.__cBearing > 180:
            self.__cBearing -= 360
        elif self.__cBearing < -180:
            self.__cBearing += 360

    def setWaypoints(self):
        # Set waypoints to default values or generate waypoints
        if self.args.USE_SAMPLE_SET:
            self.wayPoints = queue.Queue(defaultValues.SAMPLE_WP_SET[self.id])

        else:
            self.generateWaypoints()

    def setStart(self):
        # get a previous LOCATION
        self.pLoc = self.waypoints.get()

        # get a current LOCATION
        self.cLoc = self.waypoints.get()

        self.nextwp()  # and removes it from the queue

        # Calculate current and target bearing (both set to equal initially)
        self.tBearing = standardFuncs.find_bearing(self.cLoc, self.tLoc)
        self.cBearing = self.tBearing
        # logging.info("Initial bearing set to %.2f" % self.cBearing)

        # Calculate current and target elevation angles (also equal)
        self.tElevation = standardFuncs.elevation_angle(self.cLoc, self.tLoc)
        self.cElevation = self.tElevation

        # Calculate the three dimensional and two dimensional distance to target
        self.tdistance = standardFuncs.findDistance(self.cLoc, self.tLoc)

    def generateWaypoints(self):

        # Make sure the plane starting location is not within crash distance of another plane
        while (True):
            location = standardFuncs.randomLocation(self.args.GRID_SIZE[0], self.args.GRID_SIZE[1],
                                                    self.args.LOCATION)
            tooclose = [standardFuncs.findDistance(location, startLoc) <= self.args.CONFLICT_DISTANCE for startLoc
                        in Plane.startPositions]

            if not tooclose:
                self.waypoints.put(location)
                break
            else:
                print("generating new starting location", self.args.CONFLICT_DISTANCE)

        for i in range(self.numWayPoints + 1):
            location = standardFuncs.randomLocation(self.args.GRID_SIZE[0], self.args.GRID_SIZE[1],
                                                    self.args.LOCATION)
            self.waypoints.put(location)

    def updateTelemetry(self, newLoc):
        # Set the current location
        self.pLoc = self.cLoc  # Move current location to previous location
        self.cLoc = newLoc  # Set new current location

        # Calculate new elevation
        self.tBearing = standardFuncs.find_bearing(self.pLoc, self.tLoc)
        self.tElevation = standardFuncs.elevation_angle(self.pLoc, self.tLoc)

        # haversine's horizontal distance
        self.distance = standardFuncs.findDistance(newLoc, self.tLoc)

        # haversine's horizontal distance w/ vertical distance taken into account
        self.tdistance = standardFuncs.totalDistance(newLoc, self.tLoc)

        self.distanceTraveled += self.speed * self.args.DELAY

    def nextwp(self):
        self.tLoc = self.waypoints.get()

    def threatMap(self, msg):
        """
        This function is to be used by the UAV's decentralized communication thread. The purpose is to populate a map
        of threats which will be returned as a list.
        """

        for i in self.map:
            if i["ID"] == msg["ID"]:
                i["Location"] = msg["Location"]
                i["#"] = msg["#"]
                i["Dead"] = msg["Dead"]
                # logging.info("UAV #%3i map: %s" % (self.id, self.map))
                return True
        self.map.append(msg)

    # def simpleMove(self):
    #
    #     """should move in a straight line to target destination and make necessary adjustments to turning"""
    #
    # def __del__(self):
    #     if self.dead:
    #         print("UAV #", self.id, " has crashed with UAV #", self.killedBy)
    #     if self.wpAchieved == self.numWayPoints:
    #         print("UAV #", self.id, " achieved all waypoints.")
    #     pass

    def telemetry(self):
        telem = dict()
        telem["Location"] = self.cLoc
        telem["bear"] = self.cBearing
        telem["elev"] = self.cElevation
        telem["tdis"] = self.distanceTraveled
        telem["ID"] = self.id
        telem["killedBy"] = self.killedBy
        telem["Dead"] = self.dead
        return telem