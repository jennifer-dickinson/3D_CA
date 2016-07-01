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

        self.msg = {"ID": 0, "Location": ""}

        self.lastUpdate = time.time()

        # For reading the message
        self.readCounter = 0
        self.readLock = threading.RLock()
        self.broadcast = threading.Event()
        self.readTurn = threading.Event()
        self.broadcast.clear()
        self.readTurn.clear()
        self.msgRcd = threading.Event()

        # For writing the message
        self.broadcastCounter = 0
        self.msgLock = threading.RLock()
        self.broadcastWrite = threading.Event()
        self.turn = threading.Event()
        self.broadcastWrite.set()
        self.turn.clear()

        self.start()

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated: %s" % self)
        startTime = self.lastUpdate
        try:
            while self.uavsInAir>0:

                # Break if no updates within 4 seconds or no UAVs in air
                if (time.time() - self.lastUpdate >4) or self.uavsInAir <= 0:
                    logging.info("Communication timed out.")
                    break
        except KeyboardInterrupt:
            logging.info("Program interrupted by user.")

        logging.info ("Time elapsed: %f" % (time.time()-startTime))

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
        while not self.plane.dead and self.plane.wpAchieved != self.plane.numWayPoints:
            # Wait for a broadcast from UAV
            self.synch.broadcast.wait()
            logging.info ("UAV #%3i waiting for readLock" % self.plane.id)
            self.synch.readLock.acquire()

            # Read the message
            logging.info("UAV #%3i received message #%i from # %i" % (self.plane.id, self.synch.msg["#"], self.synch.msg["ID"]))
            # Increment counter for new read turn

            self.synch.readCounter += 1
            if self.synch.readCounter == self.synch.uavsInAir:
                self.synch.readCounter = 0
                self.synch.msgRcd.set()
                #logging.info("----------All UAVs received message from #%3i" % self.synch.msg["ID"])
                self.synch.broadcastWrite.set()
                self.synch.readTurn.set()
            else:
                self.synch.readTurn.clear()
                self.synch.broadcast.clear()

            self.synch.readLock.release()
            self.synch.readTurn.wait()

    def update(self):
        # Wait for it to be ok to broadcast
        self.synch.msgLock.acquire()
        self.synch.broadcastWrite.wait()
        self.synch.msgRcd.clear()
        self.synch.lastUpdate = time.time()
        logging.info ("UAV #%3i broadcasting message." % self.plane.id)

        # Send Message
        if self.plane.dead or self.plane.wpAchieved == self.plane.numWayPoints:
            self.synch.uavsInAir -= 1
            #logging.info("UAV #%3i crashed or reached all waypoints" % self.plane.id)
        else:
            self.msgCounter += 1
            self.synch.msg = {"ID": self.plane.id, "Location": self.plane.cLoc, "#" : self.msgCounter}
            # Alert UAV Comms of message
            self.synch.broadcast.set()
            # Increment counter for new turn
            self.synch.broadcastCounter += 1

            self.synch.msgRcd.wait()
            logging.info("UAV #%3i confirmed UAV Comms received message" % self.plane.id)

        if self.synch.broadcastCounter == self.synch.uavsInAir:
            self.synch.broadcastCounter = 0
            logging.info("********************UAV #%3i completed the write turn cycle." % self.plane.id)
            logging.info("##########All UAVs wrote a message")
            self.synch.turn.set()
        else:
            logging.info("**********UAV #%3i waiting for turn" % self.plane.id)
            self.synch.turn.clear()

        self.synch.msgLock.release()
        self.synch.turn.wait()
