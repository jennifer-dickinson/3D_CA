#
# This file contains all the information for planes. As of now, it only generates random planes.
# I will add
#


import random
import Queue
import standardFuncs
from defaultValues import *
import logging


# Plane object will eventually have more parameters
class Plane:
    counter = 0

    def __init__(self):
        Plane.counter += 1
        self.id = Plane.counter  # Plane ID =)

        self.speed = DEFAULT_UAV_SPEED  # UAV airspeed in meters per second, 12 meters per second by default
        self.maxElevationAngle = MAX_ELEV_ANGLE  # Maximum climbing angle in degrees
        self.minTurningRadius = MIN_TURN_RAD  # Minimum turning radius in meters, should be variable depending on speed
        self.maxBankAngle = None

        self.numWayPoints = 0  # Total number of waypoints assigned to plane
        self.wayPoints = []  # Waypoint list
        self.queue = Queue.Queue()  # Waypoint queue
        self.wpAchieved = 0  # Of waypoints achieved

        self.distance = 0  # Horizontal distance to waypoint in meters
        self.tdistance = 0  # Total distance to waypoint in meters

        self.distanceTraveled = 0  # Total distance traveled in meters

        self.sLoc = None  # Starting location in
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

    def set_cLoc(self, current_location):  # Set the current location
        self.pLoc = self.cLoc  # Move current location to previous location
        self.cLoc = current_location  # Set new current location

    def nextwp(self):
        self.tLoc = self.queue.get_nowait()


# Automatically generate planeObjects and wayPoints
# Todo: make an option to load planeObjects and wayPoints
# Todo: make option to manually set wayPoints for each plane

def generate_planes(numPlanes, numWayPoints, gridSize, communicator, location=OUR_LOCATION, ):
    plane = []  # Create list of planes

    # Creates a set number of planes
    for i in range(0, numPlanes):
        plane.append(Plane())
        plane[i].numWayPoints = numWayPoints

        logging.info("UAV #%3i generated." % plane[i].id)
        for j in range(0, plane[i].numWayPoints + 2):  # +2 to git inital and previous location

            waypoint = randomLocation(gridSize, location)

            plane[i].wayPoints.append(waypoint)
            plane[i].queue.put(plane[i].wayPoints[j])

            logging.info("UAV #%3i generated waypoint #%i at: %s" % (plane[i].id, (j + 1), waypoint))

        plane[i].set_cLoc(plane[i].queue.get_nowait())  # Set current location to first generated waypoint
        plane[i].set_cLoc(plane[i].queue.get_nowait())
        plane[i].nextwp()  # and removes it from the queue

        # Calculate current and target bearing (both set to equal initially)
        plane[i].tBearing = standardFuncs.find_bearing(plane[i].cLoc, plane[i].tLoc)
        plane[i].cBearing = plane[i].tBearing

        # Calculate current and target elevation angles (also equa)
        plane[i].tElevation = standardFuncs.elevation_angle(plane[i].cLoc, plane[i].tLoc)
        plane[i].cElevation = plane[i].tElevation

        # Calculate the three dimensional and two dimensional distance to target
        plane[i].distance = standardFuncs.findDistance(plane[i].cLoc, plane[i].tLoc)
        plane[i].tdistance = standardFuncs.totalDistance(plane[i].cLoc, plane[i].tLoc)

        if IS_TEST:
            print "Plane ID is", plane[i].id, "and has", plane[i].numWayPoints, "waypoints"
            print plane[i].wayPoints

        communicator.startUp(plane[i])

    return plane


def randomLocation(gridSize, location=OUR_LOCATION):
    # Calculates random waypoints based on provided grid and adds them to a list and queue
    grid = standardFuncs.generateGrid(gridSize, location)  # Creates a square grid centered about location
    lat = random.uniform(grid[0][0], grid[0][1])
    lon = random.uniform(grid[1][0], grid[1][1])
    alt = random.uniform(375, 400)
    location = standardFuncs.loc(lat, lon, alt)
    return location
