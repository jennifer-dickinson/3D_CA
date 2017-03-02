import logging
import threading
import time

import centralizedComm
import decentralizedComm
import planes
import standardFuncs
from maneuvers import straightLine


# Automatically generate planeObjects and wayPoints
class PlaneCollection(list):
    def __init__(self, args):
        super().__init__()
        waypoints = []
        set = range(args.NUM_PLANES)

        self.comm = centralizedComm.uavComm(args.NUM_PLANES) if args.CENTRALIZED else decentralizedComm.synchronizer(
            args.NUM_PLANES)

        # if args.USE_SAMPLE_SET:
        #     args.NUM_PLANES = len(args.SAMPLE_WP_SET)
        #     set = args.SAMPLE_WP_SET

        # Creates a set number of planes
        for i in range(args.NUM_PLANES):

            self.append(planes.Plane(args))
            waypoints.append(self[i].wayPoints)

            # If decentralized, run a thread for communication from decentralizedComm
            if not args.CENTRALIZED:
                try:
                    # logging.info("Com #%3i generated." % self[i].id)
                    planeComm = decentralizedComm.communicate(self[i], self.comm)

                except:
                    logging.fatal("Communicator failed to start for UAV #%3i" % self[i].id)
                    break

            # If centralized, pass plane parameters to centralizedComm
            else:
                self.comm.startUp(self[i])
                planeComm = None

            try:
                self[i].move = threading.Thread(target=self.move, args=(self[i], planeComm),
                                                name="UAV #%i" % self[i].id)
                self[i].move.setDaemon(True)
                logging.info("UAV #%3i plane thread generated: %s" % (self[i].id, self[i].move))
            except:
                logging.fatal("Could not generate UAV #%3i" % self[i].id)

        # Note: all UAV threads should be started after UAV objects are created to avoid errors in time difference due to random nature of threads.
        for i in range(len(self)):
            self[i].move.start()

    def __del__(self):
        time.sleep(.01)
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
                killed = "--"
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

    def move(self, plane, planeComm):
        stop = False

        while not stop and not plane.dead:

            if plane.args.COLLISION_DETECTANCE:
                # Use decentralized communication and collision detection or default to centralized.
                # Todo: set both comm methods to save plane map to plane object
                if not plane.args.CENTRALIZED:
                    uav_positions = plane.map
                else:
                    uav_positions = self.comm.receive(plane)

                for elem in uav_positions:
                    distance = standardFuncs.totalDistance(plane.cLoc, elem["Location"])
                    if distance < plane.args.CRASH_DISTANCE and elem["ID"] != plane.id and elem["Dead"] == False:
                        plane.dead = True
                        plane.killedBy = elem["ID"]
                        stop = True
                        break
                    if elem["killedBy"] == plane.id:
                        plane.dead = True
                        plane.killedBy = elem["ID"]
                        stop = True
                        break

            # Check to see if UAV has reached the waypoint or completed mission.
            if (plane.tdistance < plane.args.WAYPOINT_DISTANCE):
                plane.wpAchieved += 1
                if plane.wpAchieved < plane.numWayPoints:
                    plane.nextwp()
                logging.info("UAV #%3i reached waypoint #%i." % (plane.id, plane.wpAchieved))
            if plane.wpAchieved >= plane.numWayPoints:
                stop = True
                logging.info("UAV #%3i reached all waypoints." % plane.id)
                print("Waypoint achieved")

            straightLine.straightline(plane)

            # Broadcast telemetry through decentralized communication
            if not plane.args.CENTRALIZED:
                try:
                    planeComm.update()
                except:
                    logging.fatal("UAV #%3i cannot update to communicator thread: %s" % (plane.id, planeComm))
                    plane.dead = True

            # Update telemetry to centralized communication
            else:
                self.comm.update(plane)

