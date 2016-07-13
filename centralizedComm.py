import logging
import threading
import time

import defaultValues
import standardFuncs

standardFuncs.logger()

class uavComm(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.positions = list()
        self.stopped = False

        self.startTime = time.time()
        self.updateTime = time.time()

        self.counter = 0
        self.total_uavs = defaultValues.NUM_PLANES  # Total number of UAVs in the air
        self.steps_counter = 0

        self.turn_kill_counter = 0

        self.writeState = threading.Event()
        self.writeCounter = 0
        self.readState = threading.Event()
        self.readCounter = 0

        self.lock = threading.RLock()
        self.lock2 = threading.RLock()

        self.start()
        try:
            self.readState.set()
            logging.info('Read state set.')
        except:
            logging.error('Read state not set.')

    def run(self):
        logging.info('Communicator initialized: %s' % self)
        while not self.stopped:

            time.sleep(defaultValues.DELAY)

            # If no UAVs in air, end communicator thread.
            if self.total_uavs == 0:
                logging.info('NO UAVS IN AIR')
                break

            # If timer reaches 2 seconds without an update, end communicator thread.
            elif (time.time() - self.updateTime) > defaultValues.COMM_KILL_TIME:
                print ("Communication timed out. Please check debug.log")
                logging.error('Communication timed out')
                logging.error('UAVs still in air: %.f' % self.total_uavs)
                self.stopped = True
                break

        logging.info('Communicator terminated.')

    def startUp(self, plane):
        dict = {"ID": plane.id,
                "Location": plane.cLoc,
                "bear": plane.cBearing,
                "elev": plane.cElevation,
                "Dead": plane.dead,
                "killedBy": None,
                "wpts": 0,
                "tdis": 0
                }
        self.positions.append(dict)
        # self.total_uavs += 1
        logging.info('Initial position for UAV #%3i updated!' % plane.id)

    def update(self, plane):
        self.lock.acquire()
        logging.info('UAV #%3i acquired write lock.' % plane.id)

        # Reset timeout timer.
        self.updateTime = time.time()

        # Access positions list
        for i in self.positions:
            if i["ID"] == plane.id:
                dict = i
                break

        # Only update telemetry if UAV is still alive
        if not plane.dead and not dict["Dead"]:

            # Update telemetry
            dict["Location"] = plane.cLoc
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
        elif plane.dead or dict["Dead"]:

            self.turn_kill_counter += 1
            logging.info('UAV #%3i added to deaths by 1 (%i total).' % (plane.id, self.turn_kill_counter))

            if plane.dead and not dict["Dead"]:
                dict["Dead"] = plane.dead
                dict["killedBy"] = plane.killedBy

                #
                logging.info('UAV #%3i crashed with #%3i.' % (plane.id, dict["killedBy"]))

                for i in self.positions:
                    if i["ID"] == dict["killedBy"]:
                        dict2 = i
                        dict2["Dead"] = True
                        dict2["killedBy"] = plane.id
                        break

            # If plane is dead in telemetry, update plane status
            elif not plane.dead and dict["Dead"]:
                plane.dead = dict["Dead"]
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
