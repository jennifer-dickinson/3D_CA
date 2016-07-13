# This file contains all the information for planes. As of now, it only generates random planes.

import logging
import json
import pprint
import queue
import random
import threading

import decentralizedComm
import defaultValues
import movementSimulator
import standardFuncs


# Plane object will eventually have more parameters
class Plane:
    counter = 0

    def __init__(self):
        Plane.counter += 1
        self.id = Plane.counter  # Plane ID =)

        self.speed = defaultValues.DEFAULT_UAV_SPEED  # UAV airspeed in meters per second, 12 meters per second by default
        self.maxElevationAngle = defaultValues.MAX_ELEV_ANGLE  # Maximum climbing angle in degrees
        self.minTurningRadius = defaultValues.MIN_TURN_RAD  # Minimum turning radius in meters, should be variable depending on speed
        self.maxBankAngle = None

        self.numWayPoints = 0  # Total number of waypoints assigned to plane
        self.wayPoints = []  # Waypoint list
        self.queue = queue.Queue()  # Waypoint queue
        self.wpAchieved = 0  # Of waypoints achieved

        self.distance = 0  # Horizontal distance to waypoint in meters
        self.tdistance = 0  # Total distance to waypoint in meters

        self.distanceTraveled = 0  # Total distance traveled in meters

        self.pLoc = None  # Previous location
        self.cLoc = None  # Current location
        self.tLoc = None  # Target location. Will be swapped in queue

        self.cBearing = None  # Current bearing (Cartesian)
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

    def set_cLoc(self, current_location):  # Set the current location
        self.pLoc = self.cLoc  # Move current location to previous location
        self.cLoc = current_location  # Set new current location

    def nextwp(self):
        self.tLoc = self.queue.get_nowait()

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


# Automatically generate planeObjects and wayPoints
# Todo: make an option to load planeObjects and wayPoints
# Todo: make option to manually set wayPoints for each plane

def generate_planes(numPlanes, numWayPoints, gridSize, communicator, location=defaultValues.OUR_LOCATION, ):
    plane = []  # Create list of planes

    pp = pprint.PrettyPrinter(indent=4)

    waypoints = []

    if defaultValues.CENTRALIZED:
        communicator.total_uavs = numPlanes
    elif not defaultValues.CENTRALIZED:
        communicator.uavsInAir = numPlanes

    # Creates a set number of planes
    for i in range(0, numPlanes):
        plane.append(Plane())
        plane[i].numWayPoints = numWayPoints

        for j in range(0, plane[i].numWayPoints + 2):  # +2 to git inital location and bearing.

            waypoint = randomLocation(gridSize, location)
            plane[i].wayPoints.append(waypoint)
            plane[i].queue.put(waypoint)


        waypoints.append(plane[i].wayPoints)

        # get a previous location
        plane[i].set_cLoc(plane[i].queue.get_nowait())

        # get a current location
        plane[i].sLoc = plane[i].set_cLoc(plane[i].queue.get_nowait())
        plane[i].nextwp()  # and removes it from the queue
        d = standardFuncs.DEGREE
        current_location = "(%.7f%s, %.7f%s, %.2f)" % (
            plane[i].cLoc["Latitude"], d, plane[i].cLoc["Longitude"], d, plane[i].cLoc["Altitude"])

        logging.info("UAV #%3i set to %i waypoints, starting position %s." % (
            plane[i].id, len(plane[i].wayPoints) - 2, current_location))

        # Calculate current and target bearing (both set to equal initially)
        plane[i].tBearing = standardFuncs.find_bearing(plane[i].cLoc, plane[i].tLoc)
        plane[i].cBearing = plane[i].tBearing
        logging.info("Initial bearing set to %.2f" % plane[i].cBearing)

        # Calculate current and target elevation angles (also equa)
        plane[i].tElevation = standardFuncs.elevation_angle(plane[i].cLoc, plane[i].tLoc)
        plane[i].cElevation = plane[i].tElevation

        # Calculate the three dimensional and two dimensional distance to target
        plane[i].distance = standardFuncs.findDistance(plane[i].cLoc, plane[i].tLoc)
        plane[i].tdistance = standardFuncs.totalDistance(plane[i].cLoc, plane[i].tLoc)

        # If decentralized, run a thread for communication from decentralizedComm
        if not defaultValues.CENTRALIZED:
            try:
                logging.info("Com #%3i generated." % plane[i].id)
                planeComm = decentralizedComm.communicate(plane[i], communicator)

            except:
                logging.fatal("Communicator failed to start for UAV #%3i" % plane[i].id)

        # If centralized, pass plane parameters to centralizedComm
        else:
            communicator.startUp(plane[i])
            planeComm = None
        try:
            plane[i].move = threading.Thread(target=movementSimulator.move, args=(plane[i], communicator, planeComm),
                                             name="UAV #%i" % plane[i].id)
            plane[i].move.setDaemon(True)
            logging.info("UAV #%3i plane thread generated: %s" % (plane[i].id, plane[i].move))
        except:
            logging.fatal("Could not generate UAV #%3i" % plane[i].id)

    for i in range(len(plane)):
        plane[i].move.start()

    return plane


# Calculates random waypoints based on provided grid and adds them to a list and queue
def randomLocation(gridSize, location=defaultValues.OUR_LOCATION):
    grid = standardFuncs.generateGrid(gridSize, location)  # Creates a square grid centered about location
    lat = random.uniform(grid[0][0], grid[0][1])
    lon = random.uniform(grid[1][0], grid[1][1])
    alt = random.uniform(375, 400)
    location = {"Latitude": lat, "Longitude": lon, "Altitude": alt}
    return location
