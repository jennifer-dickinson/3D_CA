# This file contains all the information for planes. As of now, it only generates random planes.
try:
    # Python 2.7
    from Queue import Queue
except:
    # Python 3.6
    from queue import Queue


# Plane object will eventually have more parameters
class Plane:
    counter = 0

    def __init__(self, args):
        self.args = args
        Plane.counter += 1
        self.id = Plane.counter  # Plane ID =)

        self.speed = args.UAV_SPEED  # UAV airspeed in meters per second, 12 meters per second by default
        self.maxElevationAngle = args.MAX_ELEV_ANGLE  # Maximum climbing angle in degrees
        self.minTurningRadius = args.MIN_TURN_RAD  # Minimum turning radius in meters, should be variable depending on speed
        self.maxBankAngle = None

        self.numWayPoints = 0  # Total number of waypoints assigned to plane
        self.wayPoints = []  # Waypoint list
        self.queue = Queue()  # Waypoint queue
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

    def simpleMove(self):

        """should move in a straight line to target destination and make necessary adjustments to turning"""

    def __del__(self):
        if self.dead:
            print("UAV #", self.id, " has crashed with UAV #", self.killedBy)
