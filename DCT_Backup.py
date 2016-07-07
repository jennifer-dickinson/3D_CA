import threading
import standardFuncs
import logging
import time
import mutex

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates. When joined by communicate, run send then restart.
class synchronizer(threading.Thread):
    def __init__(self, numPlanes):
        threading.Thread.__init__(self, name="Global Communicator")
        # pass the class object through the plane generator to modify these values
        self.uavsInAir = numPlanes
        self.deathCount = 0

        # For reading the message
        self.broadcast = threading.Event()
        self.broadcast.clear()
        self.readCounter = 0
        self.readLock = threading.RLock()
        self.readTurn = threading.Event()
        self.readTurn.clear()
        self.readDone = threading.Event

        # For writing the message
        self.msgLock = threading.RLock()
        self.turn = threading.Event()
        self.turn.clear()
        self.broadcastCounter = 0

        self.start()

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated: %s" % self)
        self.lastupdate = time.time()

        try:
            while True:

                # Break if no updates within 4 seconds or no UAVs in air
                if (time.time() - self.lastupdate > 10) or self.uavsInAir <= 0:
                    logging.info("Communication timed out.")
                    break
        except KeyboardInterrupt:
            logging.info("Program interrupted by user.")
            pass


# In planeGenerator, each plane object will start its own communication thread to update and receive telemetry.
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer):
        self.plane = plane
        self.synch = synchronizer

        threading.Thread.__init__(self, name="UAV #%i Comm" % self.plane.id)
        self.setDaemon(True)
        self.start()
        self.msgCounter = 0

    def run(self):
        while not self.plane.dead:
            if not self.plane.dead and self.plane.wpAchieved != self.plane.numWayPoints:
                # logging.info("UAV #%3i waiting for message." % self.plane.id)
                self.synch.broadcast.wait()
                self.synch.readLock.acquire()

                if self.synch.readCounter != self.synch.uavsInAir and self.synch.turn.isSet():
                    logging.info("Read turn counter reset")
                    self.synch.readTurn.clear()

                if self.synch.broadcast.isSet() and self.synch.readCounter != self.synch.uavsInAir:
                    self.synch.broadcast.clear()

                msg = self.synch.msg
                logging.info("Com #%3i received message #%i from UAV %3i" % (self.plane.id, msg["#"], msg["ID"]))
                self.synch.readCounter += 1

                if self.synch.readCounter == self.synch.uavsInAir:
                    logging.info("----------All Comms read message, reset counter, new read turn.")
                    self.synch.readCounter = 0
                    self.synch.readTurn.set()

                self.synch.readLock.release()
                self.synch.readTurn.wait()
            else:
                break

        pass

    def update(self):

        # Wait for broadcast to be over
        while self.synch.broadcast.isSet():
            pass

        self.synch.msgLock.acquire()

        if self.plane.wpAchieved == self.plane.numWayPoints:
            self.synch.uavsInAir -= 1
            logging.info("UAV #%3i has achieved all waypoints." % self.plane.id)

        elif self.plane.dead:
            self.synch.uavsInAir -= 1
            logging.info("UAV #%3i has crashed." % self.plane.id)

        else:
            self.msgCounter += 1
            self.synch.broadcastCounter += 1

            # logging.info("UAV #%3i writing message #%i. (%i/%i)" % (
            #    self.plane.id, self.msgCounter, self.synch.broadcastCounter, self.synch.uavsInAir))

            self.synch.lastUpdate = time.time()

            self.synch.msg = {"ID": self.plane.id, "Location": self.plane.cLoc, "#": self.msgCounter}

        if self.synch.broadcastCounter == self.synch.uavsInAir:
            logging.info("---------- All UAVs wrote a message.")
            self.synch.broadcastCounter = 0
            self.synch.turn.set()

        # Alert UAV communication threads that there is a message.
        # logging.info("UAV #%3i alerted others of message" % self.plane.id)
        self.synch.broadcast.set()

        # If all UAVs broadcasted telemetry for this turn, reset the turn.
        if self.synch.uavsInAir != self.synch.broadcastCounter:
            self.synch.turn.clear()
        elif self.synch.uavsInAir == self.synch.broadcastCounter
            self.synch.turn.set()
            self.synch.readDone.wait()

        self.synch.msgLock.release()

        # Wait for other UAVs to finish broadcasing their telemetry
        # logging.info("UAV #%3i waiting for turn to broadcast." % self.plane.id)
        self.synch.turn.wait()
