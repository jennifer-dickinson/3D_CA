"""
    Copyright (C) 2018  Jennifer Salas

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

import sys

from queue import Queue

from planes import Plane
from standardFuncs import *
from animation import showPaths as video
from maneuvers.straightLine import straightline

class PlaneCollection(Queue):

    def __init__(self, args):
        super().__init__(args.NUM_PLANES)

        self.grid = generateGrid(args.GRID_SIZE[0], args.GRID_SIZE[1], args.LOCATION)
        self.args = args
        self.map = []
        self.complete = Queue(args.NUM_PLANES)
        for id in range(args.NUM_PLANES):
            newplane = Plane(id, args)
            self.map.append(newplane.telemetry())
            assert(self.map[-1] != None)
            self.put(newplane)

        self.run()
        self.report()

    def run(self):
        # run the simulation

        i = 0

        while not self.empty():

            i += 1
            sys.stdout.write('\r' + '=' * i + ' ' * (60 - i))
            sys.stdout.flush()
            if i == 60: i = 0

            plane = self.get()

            plane.updatePath()



            # Check if we are simulating collisions
            if self.args.COLLISION_DETECTANCE:

                if self.map[plane.id]["Dead"]:
                    plane.killedBy = self.map[plane.id]["killedBy"]
                    plane.dead = True

                    plane.updatePath()

                    sys.stdout.write('\r' + 'UAV #%3i crashed with #%3i\n' % (plane.id, plane.killedBy))
                    self.complete.put(plane)
                    continue

                for uav in self.map[plane.id + 1:]:

                    crashing = totalDistance(plane.cLoc, uav["Location"]) <= self.args.CRASH_DISTANCE
                    withself = uav["ID"] == plane.id
                    dead = uav["Dead"]
                    crashed = uav["killedBy"] == plane.id
                    if (crashing and not withself and not dead) or crashed:

                        # self.map[uav["ID"]]["Dead"] = True
                        self.map[uav["ID"]]["killedBy"] = plane.id
                        self.map[uav["ID"]]["Dead"] = True

                        self.map[plane.id]["killedBy"] = plane.killedBy
                        self.map[plane.id]["Dead"] = True

                        plane.dead = True
                        plane.killedBy = uav["ID"]

                        plane.updatePath()

                        sys.stdout.write('\r' + 'UAV #%3i crashed with #%3i\n' % (plane.id, uav["ID"]))
                        sys.stdout.flush()

                    # Yay, the plane didn't crash
                if plane.dead:
                    self.complete.put(plane)
                    continue
            # check if this plane has reached a waypoint
            wpflag = False
            if plane.tdistance < self.args.WAYPOINT_DISTANCE:
                sys.stdout.write('\r' + "UAV #%3i reached waypoint #%i.\n" % (plane.id, plane.wpAchieved))
                sys.stdout.flush()
                plane.wpAchieved += 1
                wpflag = True
                plane.wpflag = True

                if plane.waypoints.empty():
                    sys.stdout.write('\r' + ("UAV #%3i reached all waypoints.\n" % plane.id))
                    sys.stdout.flush()
                    self.complete.put(plane)
                    continue
                else:
                    plane.nextwp()
            else:
                plane.wpflag = False

            straightline(plane)

            assert(self.map[plane.id] != plane.telemetry())

            self.map[plane.id] = plane.telemetry()
            self.put(plane)

        print("Completed simulation")



    def report(self):
        paths = []

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

        while not self.complete.empty():
            plane = self.complete.get()
            paths.append(plane.path)

            if plane.dead:
                killed = "UAV #%s" % plane.killedBy
            else:
                killed = "--"
            location = "(%.7f%s, %.7f%s, %.1f m)" % (
                plane.cLoc["Latitude"], DEGREE,
                plane.cLoc["Longitude"], DEGREE,
                plane.cLoc["Altitude"],
            )

            time_elapsed = plane.distanceTraveled / 12

            minutes = time_elapsed / 60
            seconds = time_elapsed % 60

            actual = "%2i:%02i" % (minutes, seconds)

            print('%3i  %-40s  %6.1f  %4s  %-5s  %-10s  %10s' % (
                plane.id,
                location,
                plane.distanceTraveled,
                plane.wpAchieved,
                plane.dead,
                killed,
                actual
            ))

        print("Generating video... this may also take a while")

        video(paths)
