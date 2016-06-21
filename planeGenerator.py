#
# This file contains all the information for planes. As of now, it only generates random planes.
# I will add
#


import random
import collections
import Queue

from main import *


# Plane object will eventually have more parameters
class Plane:
    counter = 0

    def __init__(self):
        Plane.counter += 1
        self.id = Plane.counter             # Plane ID =)

        self.speed = 20                     # UAV airspeed in meters per second, 12 meters per second by default
        self.maxElevationAngle = 22       # Maximum climbing angle in degrees
        self.minTurningRadius = 12        # Minimum turning radius in meters, should be variable depending on speed, but default meters
        self.maxBankAngle = None

        self.numWayPoints = 0               # Total number of waypoints assigned to plane
        self.wayPoints = []                 # Waypoint list
        self.queue = Queue.Queue()          # Waypoint queue

        self.distance  = None               # Horizontal distance to waypoint in meters
        self.tdistance = None               # Total distance to waypoint in meters

        self.sLoc = None                    # Starting location in
        self.pLoc = None                    # Previous location
        self.cLoc = None                    # Current location
        self.tLoc = None                    # Target location. Will be swapped in queue

        self.cbearing = None                # Current bearing (Cartesian)
        self.tbearing = None                # Target bearing  (Cartesian)
        self.celevation = None              # Current elevation (Cartesian)
        self.televation = None              # Target elevation  (Cartesian)

        self.avoid = False                  # Is the plane performing an avoidance maneuver?
        self.avoidanceWaypoint = None       # Avoidance waypoint (should only be one)

    def set_cLoc(self, current_location):    # Set the current location
        self.pLoc = self.cLoc                   # Move current location to previous location
        self.cLoc = current_location             # Set new current location

    def nextwp(self):
        self.tLoc = self.queue.get_nowait()

    def set_cbearing (self, current_bearing):
        self.cbearing = current_bearing

    def set_tbearing (self, target_bearing):
        self.tbearing = target_bearing

    def set_eangle (self, elevation_angle):
        self.celevation = elevation_angle

# Automatically generate planeObjects and wayPoints
# Todo: make an option to load planeObjects and wayPoints
# Todo: make option to manually set wayPoints for each plane

def generate_planes(numPlanes, numWayPoints, gridSize, location=ourLatLon):

    grid = generateGrid(gridSize, location)     # Creates a square grid centered about location

    plane = []  # Create list of planes
    loc = collections.namedtuple('coordinate', 'latitude longitude altitude')


    # Creates a set number of planes
    for i in range(0, numPlanes):
        plane.append(Plane())
        plane[i].numWayPoints = numWayPoints

        for j in range(0, plane[i].numWayPoints + 1):        # +1 to generate initial location

            # Calculates random waypoints based on provided grid and adds them to a list and queue
            lat = random.uniform(grid[0][0], grid[0][1])
            lon = random.uniform(grid[1][0], grid[1][1])
            alt = random.uniform(375,400)
            plane[i].wayPoints.append(loc(lat,lon,alt))
            plane[i].queue.put(plane[i].wayPoints[j])

        plane[i].set_cLoc(plane[i].queue.get_nowait())  # Set current location to first generated waypoint
        plane[i].nextwp()                               # and removes it from the queue


        # Variables used to calculate other things...
        clat = plane[i].cLoc.latitude
        clon = plane[i].cLoc.longitude
        calt = plane[i].cLoc.altitude

        tlat = plane[i].tLoc.latitude
        tlon = plane[i].tLoc.longitude
        talt = plane[i].tLoc.altitude

        # Calculate current and target bearing (both set to equal initially)
        plane[i].tbearing = find_bearing(clat, clon, tlat, tlon)
        plane[i].cbearing = plane[i].tbearing

        # Calculate current and target elevation angles (also equa)
        plane[i].televation = elevation_angle(clat, clon, calt, tlat, tlon, talt)
        plane[i].celevation = plane[i].televation

        if is_test:
            print "Plane ID is", plane[i].id, "and has", plane[i].numWayPoints, "waypoints"
            print plane[i].wayPoints

    return plane