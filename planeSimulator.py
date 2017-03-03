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
import logging
import threading

import centralizedComm
import decentralizedComm
import planes
import standardFuncs
from animation import write as video
from maneuvers import straightLine


# Automatically generate planeObjects and wayPoints
class PlaneCollection(list):
    def __init__(self, args):
        super().__init__()

        self.grid = standardFuncs.generateGrid(args.GRID_SIZE[0], args.GRID_SIZE[1], args.LOCATION)
        self.set = args.NUM_PLANES

        self.comm = centralizedComm.uavComm(args.NUM_PLANES) if args.CENTRALIZED else decentralizedComm.synchronizer(
            args.NUM_PLANES)

        # Creates a set number of planes
        for id in range(args.NUM_PLANES):

            self.append(planes.Plane(args))
            # If decentralized, run a thread for communication from decentralizedComm
            if not args.CENTRALIZED:
                try:
                    # logging.info("Com #%3i generated." % self[i].id)
                    planeComm = decentralizedComm.communicate(self[id], self.comm)

                except:
                    logging.fatal("Communicator failed to start for UAV #%3i" % id)
                    break

            # If centralized, pass plane parameters to centralizedComm
            else:
                self.comm.startUp(self[id])
                planeComm = None

            try:
                self[id].move = threading.Thread(target=self.move, args=(id, planeComm),
                                                 name="UAV #%i" % id)
                self[id].move.setDaemon(True)
                logging.info("UAV #%3i plane thread generated: %s" % (id, self[id].move))
            except:
                logging.fatal("Could not generate UAV #%3i" % id)

        # Note: all UAV threads should be started after UAV objects are created to avoid errors in time difference due to random nature of threads.
        for id in range(len(self)):
            self[id].move.start()

        self.PlaneCollection()

    def PlaneCollection(self):
        return self

    def __del__(self):
        self.report()

    def report(self):
        map = []
        for id in range(self.set):
            map.append(self[id].path)
        self.uav_status()
        video(map)

    def uav_status(self):
        # Print status for each UAV.
        title = '\n%-3s  %-40s  %-6s  %-4s  %-5s  %-10s  %-10s' % (
            'ID#',
            'Final Location',
            'Dist.',
            'WPTS',
            'Dead?',
            'Killed By?',
            'Live Time'
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

            time = self[i].distanceTraveled / 12

            minutes = time / 60
            seconds = time % 60

            actual = "%2i:%02i" % (minutes, seconds)

            print('%3i  %-40s  %6.1f  %4s  %-5s  %-10s  %10s' % (
                self[i].id,
                location,
                self[i].distanceTraveled,
                self[i].wpAchieved,
                self[i].dead,
                killed,
                actual
            ))

    def move(self, id, planeComm):
        stop = False

        while not stop and not self[id].dead:

            if self[id].args.COLLISION_DETECTANCE:
                # Use decentralized communication and collision detection or default to centralized.
                # Todo: set both comm methods to save map to plane object
                if not self[id].args.CENTRALIZED:
                    uav_positions = self[id].map
                else:
                    uav_positions = self.comm.receive(self[id])

                for elem in uav_positions:
                    distance = standardFuncs.totalDistance(self[id].cLoc, elem["Location"])
                    if distance < self[id].args.CRASH_DISTANCE and elem["ID"] != id and elem["Dead"] == False:
                        self[id].dead = True
                        self[id].killedBy = elem["ID"]
                        stop = True
                        break
                    if elem["killedBy"] == id:
                        self[id].dead = True
                        self[id].killedBy = elem["ID"]
                        stop = True
                        break

            # Check to see if UAV has reached the waypoint or completed mission.
            wpflag = False
            if (self[id].tdistance < self[id].args.WAYPOINT_DISTANCE):
                self[id].wpAchieved += 1
                wpflag = True
                if self[id].wpAchieved < self[id].numWayPoints:
                    self[id].nextwp()
                logging.info("UAV #%3i reached waypoint #%i." % (id, self[id].wpAchieved))
            if self[id].wpAchieved >= self[id].numWayPoints:
                stop = True
                logging.info("UAV #%3i reached all waypoints." % id)
            straightLine.straightline(self[id])

            # Broadcast telemetry through decentralized communication
            if not self[id].args.CENTRALIZED:
                try:
                    planeComm.update()
                except:
                    logging.fatal("UAV #%3i cannot update to communicator thread: %s" % (id, planeComm))
                    self[id].dead = True

            # Update telemetry to centralized communication
            else:
                self.comm.update(self[id])

            upLoc = self[id].cLoc
            upLoc['wpflag'] = wpflag
            self[id].path.append(upLoc)
