# This file contains all the information for planes. As of now, it only generates random planes.

import logging

try:
    # Python 2.7
    from Queue import Queue
except:
    # Python 3.5
    from queue import Queue

import threading

import decentralizedComm
import planeSimulator
import standardFuncs


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


# Automatically generate planeObjects and wayPoints
class PlaneCollection(list):
    def __init__(self, args, communicator):
        waypoints = []
        set = range(0, args.NUM_PLANES)

        if args.USE_SAMPLE_SET:
            args.NUM_PLANES = len(args.SAMPLE_WP_SET)
            set = args.SAMPLE_WP_SET

        if args.CENTRALIZED:
            communicator.total_uavs = args.NUM_PLANES
        else:
            communicator.uavsInAir = args.NUM_PLANES

        # Creates a set number of planes
        i = 0
        for each in set:
            self.append(Plane(args))
            if args.USE_SAMPLE_SET:
                args.NUM_WAYPOINTS = int(len(args.SAMPLE_WP_SET[i]) - 2)
                self[i].numWayPoints = args.NUM_WAYPOINTS
                for elem in each:
                    self[i].wayPoints.append(elem)
                    self[i].queue.put(elem)
            else:

                self[i].numWayPoints = args.NUM_WAYPOINTS
                for j in range(0, self[i].numWayPoints + 2):  # +2 to get initial LOCATION and bearing.

                    waypoint = standardFuncs.randomLocation(args.GRID_SIZE[0], args.GRID_SIZE[1], args.LOCATION)
                    self[i].wayPoints.append(waypoint)
                    self[i].queue.put(waypoint)

            waypoints.append(self[i].wayPoints)

            # get a previous LOCATION
            self[i].set_cLoc(self[i].queue.get_nowait())

            # get a current LOCATION
            self[i].sLoc = self[i].set_cLoc(self[i].queue.get_nowait())
            self[i].nextwp()  # and removes it from the queue
            d = standardFuncs.DEGREE
            current_location = "(%.7f%s, %.7f%s, %.2f)" % (
                self[i].cLoc["Latitude"], d, self[i].cLoc["Longitude"], d, self[i].cLoc["Altitude"])

            logging.info("UAV #%3i set to %i waypoints, starting position %s." % (
                self[i].id, len(self[i].wayPoints) - 2, current_location))

            # Calculate current and target bearing (both set to equal initially)
            self[i].tBearing = standardFuncs.find_bearing(self[i].cLoc, self[i].tLoc)
            self[i].cBearing = self[i].tBearing
            logging.info("Initial bearing set to %.2f" % self[i].cBearing)

            # Calculate current and target elevation angles (also equal)
            self[i].tElevation = standardFuncs.elevation_angle(self[i].cLoc, self[i].tLoc)
            self[i].cElevation = self[i].tElevation

            # Calculate the three dimensional and two dimensional distance to target
            self[i].distance = standardFuncs.findDistance(self[i].cLoc, self[i].tLoc)
            self[i].tdistance = standardFuncs.totalDistance(self[i].cLoc, self[i].tLoc)

            # If decentralized, run a thread for communication from decentralizedComm
            if not args.CENTRALIZED:
                try:
                    logging.info("Com #%3i generated." % self[i].id)
                    planeComm = decentralizedComm.communicate(self[i], communicator)

                except:
                    logging.fatal("Communicator failed to start for UAV #%3i" % self[i].id)
                    break

            # If centralized, pass plane parameters to centralizedComm
            else:
                communicator.startUp(self[i])
                planeComm = None
            try:
                self[i].move = threading.Thread(target=planeSimulator.move, args=(self[i], communicator, planeComm),
                                                name="UAV #%i" % self[i].id)
                self[i].move.setDaemon(True)
                logging.info("UAV #%3i plane thread generated: %s" % (self[i].id, self[i].move))
            except:
                logging.fatal("Could not generate UAV #%3i" % self[i].id)
            i += 1

        # Note: all UAV threads should be started after UAV objects are created to avoid errors in time difference due to random nature of threads.
        for i in range(len(self)):
            self[i].move.start()

            # return self

    def __del__(self):
        self.uav_status()

    def uav_status(self):
        # Print status for each UAV.
        title = '\n%-3s  %-40s  %-6s  %-4s  %-5s  %-10s ' % (
            'ID#',
            'Final Location',
            'Dist.',
            'WPTS',
            'Dead?',
            'Killed By?'
        )
        print(title)
        line = ""
        for i in title:
            line += "_"
        print(line)

        for i in range(len(self)):
            if self[i].dead:
                killed = "UAV #%s" % self[i].killedBy
            else:
                killed = "N/A"
            location = "(%.7f%s, %.7f%s, %.1f m)" % (
                self[i].cLoc["Latitude"], standardFuncs.DEGREE,
                self[i].cLoc["Longitude"], standardFuncs.DEGREE,
                self[i].cLoc["Altitude"],
            )
            print('%3i  %-40s  %6.1f  %4s  %-5s  %-10s' % (
                self[i].id,
                location,
                self[i].distanceTraveled,
                self[i].wpAchieved,
                self[i].dead,
                killed
            ))

    # def map(self):