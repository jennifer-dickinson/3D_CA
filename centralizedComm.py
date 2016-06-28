from threading import Thread, Event, RLock
import time
from defaultValues import *
from standardFuncs import *
import logging
import sys

logger()


class uavComm(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.positions = list()
        self.stopped = False

        self.startTime = time.time()

        self.timer = 0
        self.counter = 0
        self.total_uavs = 0  # Total number of UAVs in the air
        self.steps_counter = 0

        self.turn_kill_counter = 0

        self.writeState = Event()
        self.writeCounter = 0
        self.readState = Event()
        self.readCounter = 0

        self.lock = RLock()
        self.lock2 = RLock()
        try:
            self.readState.set()
            logging.info('Read state set.')
        except:
            logging.error('Read state not set.')

    def run(self):
        print "Simulating UAV flights. This may take a while..."
        dots = ""
        while not self.stopped:

            dots += "."
            print "\r%-80s" % dots,
            sys.stdout.flush()
            if len(dots) == 80: dots = ""

            time.sleep(DELAY)

            # Increment timer with each loop. If no updates after threshold, break.
            self.timer += 1

            # If no UAVs in air, end communicator thread.
            if self.total_uavs == 0:
                logging.info('NO UAVS IN AIR')
                break

            # If timer reaches 2 seconds without an update, end communicator thread.
            elif (self.timer * DELAY) > 2:
                print ("Communication timed out. Please check debug.log")
                logging.error('Communication timed out')
                logging.error('UAVs still in air: %.f' % self.total_uavs)
                self.stopped = True
                break
        logging.info('Communication has ended.')
        time.sleep(1)
        self.uav_status()

    def startUp(self, plane):
        dict = {"ID": plane.id,
                "cLoc": plane.cLoc,
                "bear": plane.cBearing,
                "elev": plane.cElevation,
                "dead": plane.dead,
                "killedBy": None,
                "wpts": 0,
                "tdis": 0
                }
        self.positions.append(dict)
        self.timer = 0
        self.total_uavs += 1
        logging.info('Initial position for UAV #%3i updated!' % plane.id)

    def send(self, plane):
        self.lock.acquire()
        logging.info('UAV #%3i acquired write lock.' % plane.id)

        # Reset timeout timer.
        self.timer = 0  # Reset timeout timer

        # Access positions list
        dict = (item for item in self.positions if item["ID"] == plane.id).next()

        # Only update telemetry if UAV is still alive
        if not plane.dead and not dict["dead"]:
            # Update telemetry
            dict["cLoc"] = plane.cLoc
            dict["bear"] = plane.cBearing
            dict["elev"] = plane.cElevation
            dict["tdis"] = plane.distanceTraveled

            logging.info('UAV #%3i updated position' % plane.id)

            # Update waypoints achieved
            if dict["wpts"] < plane.wpAchieved:
                dict["wpts"] = plane.wpAchieved
                # Display message if waypoint achieved
                logging.info('UAV #%3i reached waypoint #%3i.' % (dict["ID"], dict["wpts"]))

        # If UAV is crashed, update status in telemetry and object
        elif plane.dead or dict["dead"]:
            self.turn_kill_counter += 1
            logging.info('UAV #%3i added to deaths by 1 (%i total).' % (plane.id, self.turn_kill_counter))
            if plane.dead and not dict["dead"]:
                dict["dead"] = plane.dead
                dict["killedBy"] = plane.killedBy

                #
                logging.info('UAV #%3i crashed with #%3i.' % (plane.id, dict["killedBy"]))
                dict2 = (item for item in self.positions if item["ID"] == dict["killedBy"]).next()
                dict2["dead"] = True
                dict2["killedBy"] = plane.id

            # If plane is dead in telemetry, update plane status
            elif not plane.dead and dict["dead"]:
                plane.dead = dict["dead"]
                plane.killedBy = dict["killedBy"]
                logging.info('UAV #%3i found out it was crashed.' % plane.id)

        # If this UAV reached all waypoints, change status to done & reduce UAVs in air.
        if plane.wpAchieved >= plane.numWayPoints:
            logging.info('UAV #%3i completed its course.' % plane.id)
            self.turn_kill_counter += 1

        self.writeCounter += 1

        logging.info('Write access counter: %i/%i' % (self.writeCounter, self.total_uavs))

        # If the counter is equal to or greater than total UAVs, switch to readState & reset counter
        if self.writeCounter >= self.total_uavs:
            logging.info("%i UAV removed this turn." % self.turn_kill_counter)
            self.total_uavs -= self.turn_kill_counter
            logging.info("Updated total UAVs in air to %i." % self.total_uavs)
            self.turn_kill_counter = 0
            self.writeCounter = 0
            self.steps_counter += 1
            self.writeState.clear()
            self.readState.set()
            logging.info('-------------SWITCHED TO READ------------')

        self.lock.release()
        logging.info('UAV #%3i released write lock' % plane.id)

        logging.info('UAV #%3i waiting for read state.' % plane.id)
        self.readState.wait()

        return True

    def receive(self, plane):
        # logging.info('UAV #%3i running read' % plane.id)
        self.lock2.acquire()
        logging.info('UAV #%3i acquired read lock.' % plane.id)

        # Get list of UAV positions.
        list = self.positions

        logging.info('UAV #%3i accessed memory' % plane.id)

        # Increment counter.
        self.readCounter += 1

        logging.info('Read access counter: %i/%i' % (self.readCounter, self.total_uavs))
        logging.info('total UAVs in air: %i' % self.total_uavs)
        # Switch to writeState if counter is equal to or greater than UAVs in the air.
        if self.readCounter >= self.total_uavs:
            self.readCounter = 0
            self.readState.clear()
            self.writeState.set()
            logging.info('------------SWITCHED TO WRITE------------')
        self.lock2.release()
        logging.info('UAV #%3i released read lock.' % plane.id)
        logging.info('UAV #%3i waiting for write state.' % plane.id)
        self.writeState.wait()
        return list

    # Ends the thread
    def stop(self):
        self.stopped = True

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
        print title
        line = ""
        for i in title:
            line += "_"
        print line
        for elem in self.positions:
            if elem["dead"]:
                killed = "UAV #%s" % elem["killedBy"]
            else:
                killed = ""
            location = "(%.7f%s, %.7f%s, %.1f m)" % (
                elem["cLoc"].latitude, DEGREE,
                elem["cLoc"].longitude, DEGREE,
                elem["cLoc"].altitude,
            )
            print '%3i  %-40s  %6s  %4s  %-5s  %-10s' % (
                elem["ID"],
                location,
                elem["tdis"],
                elem["wpts"],
                elem["dead"],
                killed
            )
