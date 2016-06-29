import threading
import standardFuncs
import logging
import time

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates. When joined by communicate, run send then restart.
class synchronizer(threading.Thread):
    def __init__(self, numPlanes):
        threading.Thread.__init__(self, name="Global Communicator")
        # pass the class object through the plane generator to modify these values
        self.uavsInAir = numPlanes
        self.deathCount = 0

        # Sync Lock
        self.inSync = threading.RLock()
        self.waitForSync = threading.Condition(self.inSync)
        self.lastupdate = time.time()
        self.updateCounter = 0

        # Message lock
        self.messageSync = threading.RLock()
        self.waitForMessage = threading.Condition(self.inSync)

        self.msg = None

        self.start()

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated: %s" % self)
        self.lastupdate = time.time()
        while True:
            # Break if
            if (time.time() - self.lastupdate > 4) or self.uavsInAir <= 0:
                logging.info("Communication timed out.")
                print ("Communication timed out. No updates received.")
                print "Total UAVs still in air: %s" % self.uavsInAir
                print "# of UAVs on couner: %s" % self.updateCounter
                print "# of UAVs crashed: %s " % self.deathCount
                break
            if self.updateCounter == self.uavsInAir:
                self.waitForSync.acquire()
                self.updateCounter = 0
                self.uavsInAir -= self.deathCount
                self.deathCount = 0
                self.waitForSync.notify_all()
                self.waitForSync.release()


# In planeGenerator, each plane object will start its own communication thread to update and receive telemetry.
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer):
        self.plane = plane
        self.timer = synchronizer
        self.test = 0

        threading.Thread.__init__(self, name="UAV #%i Comm" % self.plane.id)
        self.setDaemon(True)
        self.start()

    def run(self):
        logging.info("UAV #%3i communicator started: %s" % (self.plane.id, self))
        while not self.plane.dead:
            self.timer.waitForMessage.acquire()
            try:
                self.timer.waitForMessage.wait()
            except:
                logging.info("Could not wait for message")
            try:
                print self.timer.msg
                self.timer.waitForMessage.release()
                logging.info("UAV #%3i Message received" % self.plane.id)
            except:
                logging.info("Could not get message")

    def update(self):
        self.timer.waitForSync.acquire()

        # Send message
        logging.info("UAV# %3i sending message" % self.plane.id)
        self.test += 1
        self.timer.msg = "UAV# %3i message #%i" % (self.plane.id, self.test)

        # Notify all threads that a message is sent
        self.timer.waitForMessage.acquire()
        self.timer.waitForMessage.notify_all()
        logging.info("UAV# %3i notifying others of message" % self.plane.id)
        self.timer.waitForMessage.release()

        # Increase UAV counter & reset timer
        self.timer.lastupdate = time.time()

        self.timer.updateCounter += 1

        if self.plane.dead or self.plane.wpAchieved == self.plane.numWayPoints:
            self.timer.deathCount += 1

        try:
            self.timer.waitForSync.acquire()
            logging.info("UAV# %3i waiting for sync." % self.plane.id)
            self.timer.waitForSync.wait()
        except:
            logging.info("Could not wait for synchronization")
            pass
